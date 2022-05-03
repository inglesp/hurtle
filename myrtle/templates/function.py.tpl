_{{ fn.namespaced_name }} = import_attr("{{ fn.path }}")


@ffi.def_extern()
def {{ fn.namespaced_name }}(ctx, argc, argv):
    interface.call_function(ctx, _{{ fn.namespaced_name }}, argc, argv)
