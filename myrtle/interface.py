class Interface:
    def __init__(self, ffi, lib):
        self.ffi = ffi
        self.lib = lib
        self.sqlite3_api = lib.sqlite3_api
        self.SQLITE_TRANSIENT = ffi.cast("sqlite3_destructor_type", -1)

    def build_function(self, ctx, fn, argc, argv):
        return Function(self, ctx, fn, argc, argv)

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
    def __init__(self, interface, ctx, fn, argc, argv):
        self.interface = interface
        self.ctx = ctx
        self.fn = fn
        self.argc = argc
        self.argv = argv

    def call(self):
        py_args = [self.interface.get_py_val(self.argv[ix]) for ix in range(self.argc)]

        try:
            result = self.fn(*py_args)
        except Exception:
            self.interface.set_result_error(self.ctx, self.fn)

        self.interface.set_result(self.ctx, result)
