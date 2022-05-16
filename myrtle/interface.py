class Interface:
    def __init__(self, ffi, lib):
        self.ffi = ffi
        self.lib = lib
        self.sqlite3_api = lib.sqlite3_api
        self.SQLITE_TRANSIENT = ffi.cast("sqlite3_destructor_type", -1)

    def build_function(self, fn):
        return Function(self, fn)

    def build_virtual_table(self, table_cls):
        return VirtualTable(self, table_cls)

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
    tables = {}
    cursors = {}

    def __init__(self, interface, table_cls):
        self.ffi = interface.ffi
        self.lib = interface.lib
        self.sqlite3_api = interface.sqlite3_api
        self.table_cls = table_cls

    def table_key_from_pointer(self, ptr):
        p = self.ffi.cast("__myrtle_csv_table *", ptr)
        return p.table_key

    def table_from_pointer(self, ptr):
        key = self.table_key_from_pointer(ptr)
        return self.tables[key]

    def cursor_key_from_pointer(self, ptr):
        p = self.ffi.cast("__myrtle_csv_cursor *", ptr)
        return p.cursor_key

    def cursor_from_pointer(self, ptr):
        key = self.cursor_key_from_pointer(ptr)
        return self.cursors[key]

    def connect(self, db, pAux, argc, argv, ppVtab, pzErr):
        argv = [self.ffi.string(argv[i]).decode("utf8") for i in range(argc)]
        table = self.table_cls()
        table.parse_args(argv)
        key = len(self.tables)
        sql = f"CREATE TABLE t({', '.join(table.schema())})".encode("utf8")
        rc = self.sqlite3_api.declare_vtab(db, sql)
        if rc == self.lib.SQLITE_OK:
            ppVtab[0] = self.sqlite3_api.malloc(self.ffi.sizeof("__myrtle_csv_table"))
            pVtab = self.ffi.cast("__myrtle_csv_table *", ppVtab[0])
            pVtab.table_key = key
            self.tables[key] = table
        else:
            # TODO
            pass

        return rc

    def disconnect(self, pVtab):
        key = self.table_key_from_pointer(pVtab)
        del self.tables[key]
        self.sqlite3_api.free(pVtab)
        return self.lib.SQLITE_OK

    def open_(self, pVtab, ppCursor):
        key = len(self.cursors)
        ppCursor[0] = self.sqlite3_api.malloc(self.ffi.sizeof("__myrtle_csv_cursor"))
        pCur = self.ffi.cast("__myrtle_csv_cursor *", ppCursor[0])
        pCur.cursor_key = key
        self.cursors[key] = Cursor()
        return self.lib.SQLITE_OK

    def close_(self, cur):
        key = self.cursor_key_from_pointer(cur)
        del self.cursors[key]
        self.sqlite3_api.free(cur)
        return self.lib.SQLITE_OK

    def next_(self, cur):
        cursor = self.cursor_from_pointer(cur)

        assert cursor.generator is not None
        assert not cursor.done

        try:
            cursor.next_values = next(cursor.generator)
        except StopIteration:
            cursor.next_values = None
            cursor.done = True

        return self.lib.SQLITE_OK

    def column(self, cur, ctx, i):
        cursor = self.cursor_from_pointer(cur)
        value = cursor.next_values[i]
        SQLITE_TRANSIENT = self.ffi.cast("sqlite3_destructor_type", -1)
        self.sqlite3_api.result_text(ctx, value.encode("utf8"), -1, SQLITE_TRANSIENT)
        return self.lib.SQLITE_OK

    def row_id(self, cur, pRowid):
        # TODO
        # cursor = self.cursor_from_pointer(cur)
        pRowid[0] = 10
        return self.lib.SQLITE_OK

    def eof(self, cur):
        cursor = self.cursor_from_pointer(cur)
        return cursor.done

    def filter_(self, pVtabCursor, idxNum, idxStr, argc, argv):
        table = self.table_from_pointer(pVtabCursor.pVtab)
        cursor = self.cursor_from_pointer(pVtabCursor)
        cursor.generator = table.generator()
        self.next_(pVtabCursor)
        return self.lib.SQLITE_OK

    def best_index(self, tab, pIdxInfo):
        return self.lib.SQLITE_OK


class Cursor:
    def __init__(self):
        self.generator = None
        self.next_values = None
        self.done = False
