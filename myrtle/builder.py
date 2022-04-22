import inspect
import importlib
import os
import pathlib
import shutil

import cffi
import jinja2

DEBUG_PATH = pathlib.Path("debug")
TEMPLATES_PATH = pathlib.Path(__file__).parent / "templates"


def build_extension(name, functions=None, verbose=True):
    assert name.isalpha()

    shutil.rmtree(DEBUG_PATH, ignore_errors=True)
    os.makedirs(DEBUG_PATH)

    ctx = {
        "extension_name": name,
        "functions": [
            function_ctx(name, path) for name, path in (functions or {}).items()
        ],
    }

    ffi = cffi.FFI()
    ffi.embedding_api(render_template("plugin_api.h", ctx))
    ffi.embedding_init_code(render_template("plugin.py", ctx))
    ffi.set_source(name, render_template("plugin.c", ctx))
    ffi.compile(verbose=verbose)

    os.rename(name + ".c", DEBUG_PATH / (name + ".c"))
    os.rename(name + ".o", DEBUG_PATH / (name + ".o"))


def render_template(name, ctx):
    with open(TEMPLATES_PATH / (name + ".tpl")) as f:
        tpl = jinja2.Template(f.read())

    rendered = tpl.render(ctx)

    with open(DEBUG_PATH / name, "w") as f:
        f.write(rendered)

    return rendered


def import_attr(dotted_path):
    try:
        module_path, attr_name = dotted_path.rsplit(".", 1)
    except ValueError:
        msg = "%s doesn't look like a module path" % dotted_path
        raise ImportError(msg)

    module = importlib.import_module(module_path)

    try:
        return getattr(module, attr_name)
    except AttributeError:
        msg = 'Module "%s" does not define "%s"' % (module_path, attr_name)
        raise ImportError(msg)


def common_ctx(name, path):
    return {
        "name": name,
        "namespaced_name": f"__myrtle_{name}",
        "path": path,
    }


def function_ctx(name, path):
    fn = import_attr(path)
    sig = inspect.signature(fn)
    params = sig.parameters.values()

    if any(p.kind.name in ["KEYWORD_ONLY", "VAR_KEYWORD"] for p in params):
        raise ValueError("Cannot create function with keyword arguments")

    if any(p.kind.name == "VAR_POSITIONAL" for p in params):
        num_args = -1
    else:
        num_args = len(params)

    return common_ctx(name, path) | {"num_args": num_args}
