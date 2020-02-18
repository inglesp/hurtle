import json

from seriespy import ffi, lib
from seriespy.lib import sqlite3_api

from vtab_generator import generate_series

VISIBLE_COL_NAMES = ["value"]
HIDDEN_COL_NAMES = ["start", "stop", "step"]
COL_NAMES = VISIBLE_COL_NAMES + HIDDEN_COL_NAMES


class Cursor:
    next_key = 0
    cursors = {}

    @classmethod
    def open(cls):
        key = cls.next_key
        cls.next_key += 1
        cls.cursors[key] = cls(key)
        return key

    @classmethod
    def from_ptr(cls, ptr):
        p = ffi.cast("series_cursor *", ptr)
        return cls.cursors[p.cursor_key]

    def __init__(self, key):
        self.key = key
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
        del self.cursors[self.key]


def connect(db, pAux, argc, argv, ppVtab, pzErr):
    visible_col_defs = ", ".join(col_name for col_name in VISIBLE_COL_NAMES)
    hidden_col_defs = ", ".join(col_name + " hidden" for col_name in HIDDEN_COL_NAMES)
    sql = f"CREATE TABLE t({visible_col_defs}, {hidden_col_defs})".encode("utf8")
    rc = sqlite3_api.declare_vtab(db, sql)
    if rc == lib.SQLITE_OK:
        ppVtab[0] = sqlite3_api.malloc(ffi.sizeof("sqlite3_vtab"))

    return rc


def disconnect(pVtab):
    sqlite3_api.free(pVtab)
    return lib.SQLITE_OK


def open_(p, ppCursor):
    ppCursor[0] = sqlite3_api.malloc(ffi.sizeof("series_cursor"))
    pCur = ffi.cast("series_cursor *", ppCursor[0])
    pCur.cursor_key = Cursor.open()
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

    try:
        cursor.hidden_values = [params[col_name] for col_name in HIDDEN_COL_NAMES]
    except KeyError:
        return lib.SQLITE_ERROR

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
