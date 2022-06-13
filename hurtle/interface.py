import inspect
import json
from enum import IntEnum


# From sqlite3.h, eg SQLITE_INDEX_CONSTRAINT_EQ
class IndexConstraint(IntEnum):
    EQ = 2
    GT = 4
    LE = 8
    LT = 16
    GE = 32
    MATCH = 64
    LIKE = 65
    GLOB = 66
    REGEXP = 67
    NE = 68
    ISNOT = 69
    ISNOTNULL = 70
    ISNULL = 71
    IS = 72
    LIMIT = 73
    OFFSET = 74
    FUNCTION = 150


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
        self.interface = interface
        self.ffi = interface.ffi
        self.lib = interface.lib
        self.sqlite3_api = interface.sqlite3_api
        self.table_cls = table_cls

    def table_key_from_pointer(self, ptr):
        p = self.ffi.cast("__hurtle_table *", ptr)
        return p.table_key

    def table_from_pointer(self, ptr):
        key = self.table_key_from_pointer(ptr)
        return self.tables[key]

    def cursor_key_from_pointer(self, ptr):
        p = self.ffi.cast("__hurtle_cursor *", ptr)
        return p.cursor_key

    def cursor_from_pointer(self, ptr):
        key = self.cursor_key_from_pointer(ptr)
        return self.cursors[key]

    def connect(self, db, pAux, argc, argv, ppVtab, pzErr):
        argv = [self.ffi.string(argv[i]).decode("utf8") for i in range(argc)]
        module_name, database_name, table_name, *argv = argv
        kwargs = dict(arg.split("=") for arg in argv)
        table = self.table_cls(**kwargs)
        sql = f"CREATE TABLE t({', '.join(table.schema)})".encode("utf8")
        rc = self.sqlite3_api.declare_vtab(db, sql)
        if rc == self.lib.SQLITE_OK:
            ppVtab[0] = self.sqlite3_api.malloc(self.ffi.sizeof("__hurtle_table"))
            pVtab = self.ffi.cast("__hurtle_table *", ppVtab[0])
            key = len(self.tables)
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
        ppCursor[0] = self.sqlite3_api.malloc(self.ffi.sizeof("__hurtle_cursor"))
        pCur = self.ffi.cast("__hurtle_cursor *", ppCursor[0])
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
        self.interface.set_result(ctx, value)
        return self.lib.SQLITE_OK

    def row_id(self, cur, pRowid):
        # TODO
        # cursor = self.cursor_from_pointer(cur)
        pRowid[0] = 10
        return self.lib.SQLITE_OK

    def eof(self, cur):
        cursor = self.cursor_from_pointer(cur)
        return cursor.done

    def best_index(self, tab, pIdxInfo):
        table = self.table_from_pointer(tab)

        constraints = parse_constraints(
            table, pIdxInfo.nConstraint, pIdxInfo.aConstraint
        )

        candidates = {}
        for method_name, method in inspect.getmembers(table, inspect.ismethod):
            if not method_name.startswith("select"):
                continue

            constraint_ixs = get_usable_constraint_ixs(method, constraints)
            if constraint_ixs is not None:
                candidates[method_name] = constraint_ixs

        if not candidates:
            # Given constraints are insufficient to resolve query.
            return self.lib.SQLITE_CONSTRAINT

        # Choose method that uses most constraints.  We can do better!
        method_name, usable_constraint_ixs = max(
            candidates.items(), key=lambda candidate: (len(candidate[1]), candidate[0])
        )

        for ix in usable_constraint_ixs:
            pIdxInfo.aConstraintUsage[ix].argvIndex = ix + 1

        idx_data = {"method_name": method_name, "constraints": constraints}
        idx_str = json.dumps(idx_data).encode("utf8")
        l = len(idx_str) + 1
        s = self.sqlite3_api.malloc(l)
        self.ffi.memmove(s, idx_str, l)
        pIdxInfo.idxStr = s
        pIdxInfo.needToFreeIdxStr = True

        return self.lib.SQLITE_OK

    def filter_(self, pVtabCursor, idxNum, idxStr, argc, argv):
        table = self.table_from_pointer(pVtabCursor.pVtab)
        cursor = self.cursor_from_pointer(pVtabCursor)
        idx_data = json.loads(self.ffi.string(idxStr))
        constraints = idx_data["constraints"]
        exprs = [self.interface.get_py_val(argv[i]) for i in range(argc)]
        kwargs = {param_name: exprs[ix] for param_name, ix in constraints.items()}
        method = getattr(table, idx_data["method_name"])
        cursor.generator = method(**kwargs)
        self.next_(pVtabCursor)
        return self.lib.SQLITE_OK


class Cursor:
    def __init__(self):
        self.generator = None
        self.next_values = None
        self.done = False


def parse_constraints(table, nConstraint, aConstraint):
    constraints = {}

    for ix in range(nConstraint):
        pConstraint = aConstraint[ix]
        # TODO: what if constraint is not usable?
        if pConstraint.op in [IndexConstraint.LIMIT, IndexConstraint.OFFSET]:
            continue
        col_name = table.schema[pConstraint.iColumn]
        if pConstraint.op == IndexConstraint.EQ:
            param_name = col_name
        else:
            op_name = IndexConstraint(pConstraint.op).name.lower()
            param_name = f"{col_name}__{op_name}"
        constraints[param_name] = ix

    return constraints


def get_usable_constraint_ixs(method, constraints):
    sig = inspect.signature(method)
    for name, param in sig.parameters.items():
        if param.default == inspect._empty and name not in constraints:
            # There's no constraint for a required parameter, so these constraints are
            # not usable.
            return
    return [
        ix for param_name, ix in constraints.items() if param_name in sig.parameters
    ]
