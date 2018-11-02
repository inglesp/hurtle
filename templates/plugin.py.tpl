from importlib import import_module

from {{ extension_name }} import ffi, lib
from {{ extension_name }}.lib import sqlite3_api

SQLITE_TRANSIENT = ffi.cast('sqlite3_destructor_type', -1)


def build_null_arg(arg):
    return None


def build_str_arg(arg):
    return ffi.string(sqlite3_api.value_text(arg)).decode('utf8')


def build_int_arg(arg):
    return sqlite3_api.value_int64(arg)


py_arg_builders = {
    lib.SQLITE_NULL: lambda arg: build_null_arg,
    lib.SQLITE_TEXT: build_str_arg,
    lib.SQLITE_INTEGER: build_int_arg,
}


def build_py_args(argc, argv):
    py_args = []
    for ix in range(argc):
        arg = argv[ix]
        value_type = sqlite3_api.value_type(arg)
        value = py_arg_builders[value_type](arg)
        py_args.append(value)
    return py_args


def set_result_null(ctx, res):
    pass


def set_result_text(ctx, res):
    sqlite3_api.result_text(ctx, res.encode('utf8'), -1, SQLITE_TRANSIENT)


def set_result_int(ctx, res):
    sqlite3_api.result_int64(ctx, res)


result_setters = {
    type(None): set_result_null,
    str: set_result_text,
    int: set_result_int,
}


def set_result(ctx, result):
    result_setters[type(result)](ctx, result)


def set_result_error(ctx, fn):
    sqlite3_api.result_error(ctx, f'An exception occurred in {fn.__name__}'.encode('utf8'), -1)


def import_attr(dotted_path):
    try:
        module_path, attr_name = dotted_path.rsplit('.', 1)
    except ValueError:
        msg = "%s doesn't look like a module path" % dotted_path
        raise ImportError(msg)

    module = import_module(module_path)

    try:
        return getattr(module, attr_name)
    except AttributeError:
        msg = 'Module "%s" does not define "%s"' % (
            module_path, attr_name)
        raise ImportError(msg)


def call_function(fn, ctx, argc, argv):
    py_args = build_py_args(argc, argv)

    try:
        result = fn(*py_args)
    except:
        set_result_error(ctx, fn)
        raise

    set_result(ctx, result)


{% for fn in functions %}
_{{ fn.namespaced_name }} = import_attr('{{ fn.path }}')


@ffi.def_extern()
def {{ fn.namespaced_name }}(ctx, argc, argv):
    call_function(_{{ fn.namespaced_name }}, ctx, argc, argv)
{% endfor %}
