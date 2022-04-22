def call_function(ffi, lib, fn, ctx, argc, argv):
    sqlite3_api = lib.sqlite3_api
    SQLITE_TRANSIENT = ffi.cast("sqlite3_destructor_type", -1)

    def _call_function(ctx, argc, argv):
        py_args = [get_py_val(argv[ix]) for ix in range(argc)]

        try:
            result = fn(*py_args)
        except Exception:
            set_result_error(ctx, fn)

        set_result(ctx, result)

    def get_py_val(sqlite_value):
        sqlite_type = sqlite3_api.value_type(sqlite_value)
        getters = {
            lib.SQLITE_INTEGER: get_int_val,
            lib.SQLITE_TEXT: get_str_val,
        }
        return getters[sqlite_type](sqlite_value)

    def get_int_val(sqlite_value):
        return sqlite3_api.value_int64(sqlite_value)

    def get_str_val(sqlite_value):
        return ffi.string(sqlite3_api.value_text(sqlite_value)).decode("utf8")

    def set_result(ctx, result):
        setters = {
            int: set_result_int,
            str: set_result_text,
        }
        return setters[type(result)](ctx, result)

    def set_result_int(ctx, result):
        sqlite3_api.result_int64(ctx, result)

    def set_result_text(ctx, result):
        sqlite3_api.result_text(ctx, result.encode("utf8"), -1, SQLITE_TRANSIENT)

    def set_result_error(ctx, fn):
        sqlite3_api.result_error(
            ctx, f"An exception occurred in {fn.__name__}".encode("utf8"), -1
        )

    _call_function(ctx, argc, argv)
