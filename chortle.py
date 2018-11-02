import inspect
import importlib
import os
import pathlib
import shutil

import attr
import cffi
import jinja2


def import_attr(dotted_path):
    try:
        module_path, attr_name = dotted_path.rsplit('.', 1)
    except ValueError:
        msg = "%s doesn't look like a module path" % dotted_path
        raise ImportError(msg)

    module = importlib.import_module(module_path)

    try:
        return getattr(module, attr_name)
    except AttributeError:
        msg = 'Module "%s" does not define "%s"' % (
            module_path, attr_name)
        raise ImportError(msg)


@attr.s
class Function:
    name = attr.ib()
    path = attr.ib()
    num_args = attr.ib()

    @property
    def namespaced_name(self):
        return f'__chortle_{self.name}'


@attr.s
class ExtensionBuilder:
    name = attr.ib()
    verbose = attr.ib(default=False)
    functions = attr.ib(default=attr.Factory(list))

    def add_function(self, name, path):
        fn = import_attr(path)
        sig = inspect.signature(fn)
        params = sig.parameters.values()

        if any(p.kind.name in ['KEYWORD_ONLY', 'VAR_KEYWORD'] for p in params):
            raise ValueError('Cannot create function with keyword arguments')

        if any(p.kind.name == 'VAR_POSITIONAL' for p in params):
            num_args = -1
        else:
            num_args = len(params)

        self.functions.append(Function(name, path, num_args))

    def load_template(self, name):
        ctx = {
            'extension_name': self.name,
            'functions': self.functions,
        }

        with open(self.templates_path / (name + '.tpl')) as f:
            tpl = jinja2.Template(f.read())

        rendered = tpl.render(ctx)

        with open(self.debug_path / name, 'w') as f:
            f.write(rendered)

        return rendered

    @property
    def debug_path(self):
        return pathlib.Path('debug')

    @property
    def templates_path(self):
        return pathlib.Path('templates')

    def build(self):
        shutil.rmtree(self.debug_path, ignore_errors=True)
        os.makedirs(self.debug_path)

        ffibuilder = cffi.FFI()
        ffibuilder.embedding_api(self.load_template('plugin_api.h'))
        ffibuilder.embedding_init_code(self.load_template('plugin.py'))
        ffibuilder.set_source(self.name, self.load_template('plugin.c'))
        ffibuilder.compile(verbose=self.verbose)

        os.rename(self.name + '.c', self.debug_path / (self.name + '.c'))
        os.rename(self.name + '.o', self.debug_path / (self.name + '.o'))
