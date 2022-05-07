_{{ fn.namespaced_name }} = interface.build_function(import_attr("{{ fn.path }}"))


@ffi.def_extern()
def {{ fn.namespaced_name }}(ctx, argc, argv):
    _{{ fn.namespaced_name }}.call(ctx, argc, argv)
