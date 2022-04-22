from myrtle.helpers import import_attr, call_function

from {{ extension_name }} import ffi, lib

{% for fn in functions %}
_{{ fn.namespaced_name }} = import_attr('{{ fn.path }}')


@ffi.def_extern()
def {{ fn.namespaced_name }}(ctx, argc, argv):
    call_function(ffi, lib, _{{ fn.namespaced_name }}, ctx, argc, argv)

{% endfor %}
