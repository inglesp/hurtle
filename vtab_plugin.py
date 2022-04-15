import csv

from csvpy import ffi, lib
from csvpy.lib import sqlite3_api

SQLITE_TRANSIENT = ffi.cast("sqlite3_destructor_type", -1)


class Impl:
    def __init__(self, argv):
        print(argv)
        k, v = argv[3].split("=")
        assert k == "filename"
        self.filename = v

    def schema(self):
        return ["code", "term"]

    def generator(self):
        with open(self.filename) as f:
            reader = csv.reader(f)
            for row in reader:
                yield row


class Table:
    tables = {}

    @classmethod
    def connect(cls, impl):
        key = len(cls.tables)
        table = cls(key, impl)
        cls.tables[key] = table
        return table

    @classmethod
    def from_ptr(cls, ptr):
        p = ffi.cast("csv_table *", ptr)
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
    def from_ptr(cls, ptr):
        p = ffi.cast("csv_cursor *", ptr)
        pVtab = ffi.cast("csv_table *", p.base.pVtab)
        table = Table.from_ptr(pVtab)
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


def connect(db, pAux, argc, argv, ppVtab, pzErr):
    argv = [ffi.string(argv[i]).decode("utf8") for i in range(argc)]
    impl = Impl(argv)
    table = Table.connect(impl)
    sql = f"CREATE TABLE t({', '.join(impl.schema())})".encode("utf8")
    print(sql)

    rc = sqlite3_api.declare_vtab(db, sql)
    if rc == lib.SQLITE_OK:
        ppVtab[0] = sqlite3_api.malloc(ffi.sizeof("csv_table"))
        pVtab = ffi.cast("csv_table *", ppVtab[0])
        pVtab.table_key = table.key

    return rc


def disconnect(pVtab):
    Table.from_ptr(pVtab).disconnect()
    sqlite3_api.free(pVtab)
    return lib.SQLITE_OK


def open_(pVtab, ppCursor):
    table = Table.from_ptr(pVtab)
    ppCursor[0] = sqlite3_api.malloc(ffi.sizeof("csv_cursor"))
    pCur = ffi.cast("csv_cursor *", ppCursor[0])
    pCur.cursor_key = Cursor.open(table.key)
    return lib.SQLITE_OK


def close_(cur):
    Cursor.from_ptr(cur).close()
    sqlite3_api.free(cur)
    return lib.SQLITE_OK


def next_(cur):
    cursor = Cursor.from_ptr(cur)
    cursor.step()
    return lib.SQLITE_OK


def column(cur, ctx, i):
    cursor = Cursor.from_ptr(cur)
    value = cursor.next_values[i]
    sqlite3_api.result_text(ctx, value.encode("utf8"), -1, SQLITE_TRANSIENT)
    return lib.SQLITE_OK


def row_id(cur, pRowid):
    cursor = Cursor.from_ptr(cur)
    # TODO
    pRowid[0] = 10
    return lib.SQLITE_OK


def eof(cur):
    cursor = Cursor.from_ptr(cur)
    return cursor.done


def filter_(pVtabCursor, idxNum, idxStr, argc, argv):
    cursor = Cursor.from_ptr(pVtabCursor)
    cursor.generator = cursor.table.impl.generator()
    cursor.step()
    return lib.SQLITE_OK


def best_index(tab, pIdxInfo):
    return lib.SQLITE_OK
