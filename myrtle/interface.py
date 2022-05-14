class Interface:
    def __init__(self, ffi, lib):
        self.ffi = ffi
        self.lib = lib
        self.sqlite3_api = lib.sqlite3_api
        self.SQLITE_TRANSIENT = ffi.cast("sqlite3_destructor_type", -1)

    def build_function(self, fn):
        return Function(self, fn)

    def build_virtual_table(self, table):
        return VirtualTable(self, table)

    def get_py_val(self, sqlite_value):
        sqlite_type = self.sqlite3_api.value_type(sqlite_value)
        getters = {
            self.lib.SQLITE_INTEGER: self.get_int_val,
            self.lib.SQLITE_TEXT: self.get_str_val,
        }
        return getters[sqlite_type](sqlite_value)

    def get_int_val(self, sqlite_value):
        return self.sqlite3_api.value_int64(sqlite_value)

    def get_str_val(self, sqlite_value):
        return self.ffi.string(self.sqlite3_api.value_text(sqlite_value)).decode("utf8")

    def set_result(self, ctx, result):
        setters = {
            int: self.set_result_int,
            str: self.set_result_text,
        }
        return setters[type(result)](ctx, result)

    def set_result_int(self, ctx, result):
        self.sqlite3_api.result_int64(ctx, result)

    def set_result_text(self, ctx, result):
        self.sqlite3_api.result_text(
            ctx, result.encode("utf8"), -1, self.SQLITE_TRANSIENT
        )

    def set_result_error(self, ctx, fn):
        self.sqlite3_api.result_error(
            ctx, f"An exception occurred in {fn.__name__}".encode("utf8"), -1
        )


class Function:
    def __init__(self, interface, fn):
        self.interface = interface
        self.fn = fn

    def call(self, ctx, argc, argv):
        py_args = [self.interface.get_py_val(argv[ix]) for ix in range(argc)]

        try:
            result = self.fn(*py_args)
        except Exception:
            self.interface.set_result_error(ctx, self.fn)

        self.interface.set_result(ctx, result)


class VirtualTable:
    def __init__(self, interface, table):
        self.ffi = interface.ffi
        self.lib = interface.lib
        self.sqlite3_api = interface.sqlite3_api
        self.table = table

    def connect(self, db, pAux, argc, argv, ppVtab, pzErr):
        argv = [self.ffi.string(argv[i]).decode("utf8") for i in range(argc)]
        impl = self.table(argv)
        table = Table.connect(impl)
        sql = f"CREATE TABLE t({', '.join(impl.schema())})".encode("utf8")
        print(sql)

        rc = self.sqlite3_api.declare_vtab(db, sql)
        if rc == self.lib.SQLITE_OK:
            ppVtab[0] = self.sqlite3_api.malloc(self.ffi.sizeof("__myrtle_csv_table"))
            pVtab = self.ffi.cast("__myrtle_csv_table *", ppVtab[0])
            pVtab.table_key = table.key

        return rc

    def disconnect(self, pVtab):
        Table.from_ptr(self.ffi, pVtab).disconnect()
        self.sqlite3_api.free(pVtab)
        return self.lib.SQLITE_OK

    def open_(self, pVtab, ppCursor):
        table = Table.from_ptr(self.ffi, pVtab)
        ppCursor[0] = self.sqlite3_api.malloc(self.ffi.sizeof("__myrtle_csv_cursor"))
        pCur = self.ffi.cast("__myrtle_csv_cursor *", ppCursor[0])
        pCur.cursor_key = Cursor.open(table.key)
        return self.lib.SQLITE_OK

    def close_(self, cur):
        Cursor.from_ptr(self.ffi, cur).close()
        self.sqlite3_api.free(cur)
        return self.lib.SQLITE_OK

    def next_(self, cur):
        cursor = Cursor.from_ptr(self.ffi, cur)
        cursor.step()
        return self.lib.SQLITE_OK

    def column(self, cur, ctx, i):
        cursor = Cursor.from_ptr(self.ffi, cur)
        value = cursor.next_values[i]
        SQLITE_TRANSIENT = self.ffi.cast("sqlite3_destructor_type", -1)
        self.sqlite3_api.result_text(ctx, value.encode("utf8"), -1, SQLITE_TRANSIENT)
        return self.lib.SQLITE_OK

    def row_id(self, cur, pRowid):
        # TODO
        # cursor = Cursor.from_ptr(self.ffi, cur)
        pRowid[0] = 10
        return self.lib.SQLITE_OK

    def eof(self, cur):
        cursor = Cursor.from_ptr(self.ffi, cur)
        return cursor.done

    def filter_(self, pVtabCursor, idxNum, idxStr, argc, argv):
        cursor = Cursor.from_ptr(self.ffi, pVtabCursor)
        cursor.generator = cursor.table.impl.generator()
        cursor.step()
        return self.lib.SQLITE_OK

    def best_index(self, tab, pIdxInfo):
        return self.lib.SQLITE_OK


class Table:
    tables = {}

    @classmethod
    def connect(cls, impl):
        key = len(cls.tables)
        table = cls(key, impl)
        cls.tables[key] = table
        return table

    @classmethod
    def from_ptr(cls, ffi, ptr):
        p = ffi.cast("__myrtle_csv_table *", ptr)
        return cls.tables[p.table_key]

    def __init__(self, key, impl):
        self.key = key
        self.impl = impl
        self.cursors = {}

    def disconnect(self):
        del self.tables[self.key]


class Cursor:
    @classmethod
    def open(cls, table_key):
        table = Table.tables[table_key]
        cursor_key = len(table.cursors)
        table.cursors[cursor_key] = cls(cursor_key, table)
        return cursor_key

    @classmethod
    def from_ptr(cls, ffi, ptr):
        p = ffi.cast("__myrtle_csv_cursor *", ptr)
        pVtab = ffi.cast("__myrtle_csv_table *", p.base.pVtab)
        table = Table.from_ptr(ffi, pVtab)
        return table.cursors[p.cursor_key]

    def __init__(self, key, table):
        self.key = key
        self.table = table
        self.generator = None
        self.next_values = None
        self.done = False

    def step(self):
        assert self.generator is not None
        assert not self.done

        try:
            self.next_values = next(self.generator)
        except StopIteration:
            self.next_values = None
            self.done = True

    def close(self):
        del self.table.cursors[self.key]
