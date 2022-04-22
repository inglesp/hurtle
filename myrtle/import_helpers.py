from importlib import import_module


def import_attr(dotted_path):
    try:
        module_path, attr_name = dotted_path.rsplit(".", 1)
    except ValueError:
        msg = f"'{dotted_path}' doesn't look like a module path"
        raise ImportError(msg)

    module = import_module(module_path)

    try:
        return getattr(module, attr_name)
    except AttributeError:
        msg = f"Module '{module_path}' does not define '{attr_name}'"
        raise ImportError(msg)
