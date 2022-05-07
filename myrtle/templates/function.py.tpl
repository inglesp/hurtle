_{{ fn.namespaced_name }} = import_attr("{{ fn.path }}")


@ffi.def_extern()
def {{ fn.namespaced_name }}(ctx, argc, argv):
    function = interface.build_function(ctx, _{{ fn.namespaced_name }}, argc, argv)
    function.call()
