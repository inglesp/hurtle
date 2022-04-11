import json

from csvpy import ffi, lib
from csvpy.lib import sqlite3_api

from vtab_generator import generate_series

VISIBLE_COL_NAMES = ["value"]
HIDDEN_COL_NAMES = ["start", "stop", "step"]
COL_NAMES = VISIBLE_COL_NAMES + HIDDEN_COL_NAMES


class Table:
    tables = {}

    @classmethod
    def connect(cls, params):
        key = len(cls.tables)
        cls.tables[key] = cls(key, params)
        return key

    @classmethod
    def from_ptr(cls, ptr):
        p = ffi.cast("csv_table *", ptr)
        return cls.tables[p.table_key]

    def __init__(self, key, params):
        self.key = key
        self.params = params
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
        self.next_value = None
        self.hidden_values = None
        self.done = False

    def step(self):
        assert self.generator is not None
        assert not self.done

        try:
            self.next_value = next(self.generator)
        except StopIteration:
            self.done = True

    def close(self):
        del self.table.cursors[self.key]


def connect(db, pAux, argc, argv, ppVtab, pzErr):
    visible_col_defs = ", ".join(col_name for col_name in VISIBLE_COL_NAMES)
    hidden_col_defs = ", ".join(col_name + " hidden" for col_name in HIDDEN_COL_NAMES)
    sql = f"CREATE TABLE t({visible_col_defs}, {hidden_col_defs})".encode("utf8")

    params = {}
    try:
        for i in range(3, argc):
            arg = ffi.string(argv[i]).decode("utf8")
            key, value = arg.split("=")
            if key not in HIDDEN_COL_NAMES:
                return lib.SQLITE_ERROR
            params[key] = int(value)
    except ValueError:
        return lib.SQLITE_ERROR

    rc = sqlite3_api.declare_vtab(db, sql)
    if rc == lib.SQLITE_OK:
        ppVtab[0] = sqlite3_api.malloc(ffi.sizeof("csv_table"))
        pVtab = ffi.cast("csv_table *", ppVtab[0])
        pVtab.table_key = Table.connect(params)

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
    values = [cursor.next_value] + cursor.hidden_values
    sqlite3_api.result_int64(ctx, values[i])
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

    idx_data = json.loads(ffi.string(idxStr))
    constraints = idx_data["constraints"]
    order_bys = idx_data["order_bys"]
    exprs = [sqlite3_api.value_int64(argv[i]) for i in range(argc)]

    params = {"step": 1}

    for k, v in cursor.table.params.items():
        params[k] = v

    for constraint, expr in zip(constraints, exprs):
        params[constraint["col_name"]] = expr

    params["order_by"] = []

    for order_by in order_bys:
        col_name = order_by["col_name"]
        if col_name in VISIBLE_COL_NAMES:
            if order_by["desc"]:
                params["order_by"].append(f"-{col_name}")
            else:
                params["order_by"].append(col_name)

            break

    cursor.hidden_values = [params[col_name] for col_name in HIDDEN_COL_NAMES]
    cursor.generator = generate_series(**params)
    cursor.step()

    return lib.SQLITE_OK


def best_index(tab, pIdxInfo):
    constraints = parse_constraints(pIdxInfo.nConstraint, pIdxInfo.aConstraint)
    constrained_col_names = [c["col_name"] for c in constraints]

    for constraint in constraints:
        constraint_ix = constraint["constraint_ix"]
        pIdxInfo.aConstraintUsage[constraint_ix].argvIndex = constraint_ix + 1

    order_bys = parse_order_bys(pIdxInfo.nOrderBy, pIdxInfo.aOrderBy)

    for order_by in order_bys:
        if order_by["col_name"] in VISIBLE_COL_NAMES:
            pIdxInfo.orderByConsumed = True

    idx_data = {"constraints": constraints, "order_bys": order_bys}
    # print(idx_data)

    idx_str = json.dumps(idx_data).encode("utf8")
    l = len(idx_str) + 1
    s = sqlite3_api.malloc(l)
    ffi.memmove(s, idx_str, l)
    pIdxInfo.idxStr = s
    pIdxInfo.needToFreeIdxStr = True

    return lib.SQLITE_OK


def parse_constraints(nConstraint, aConstraint):
    constraints = []

    for ix in range(nConstraint):
        pConstraint = aConstraint[ix]
        constraints.append(
            {
                "constraint_ix": ix,
                "col_ix": pConstraint.iColumn,
                "col_name": COL_NAMES[pConstraint.iColumn],
                "usable": pConstraint.usable,
                "op": pConstraint.op,
            }
        )

    return constraints


def parse_order_bys(nOrderBy, aOrderBy):
    order_bys = []

    for ix in range(nOrderBy):
        pOrderBy = aOrderBy[ix]
        order_bys.append(
            {
                "order_by_ix": ix,
                "col_ix": pOrderBy.iColumn,
                "col_name": COL_NAMES[pOrderBy.iColumn],
                "desc": pOrderBy.desc,
            }
        )

    return order_bys
