from myrtle.import_helpers import import_attr
from myrtle.interface import Interface

from {{ extension_name }} import ffi, lib

interface = Interface(ffi, lib)

{% for fn in functions %}
_{{ fn.namespaced_name }} = import_attr('{{ fn.path }}')


@ffi.def_extern()
def {{ fn.namespaced_name }}(ctx, argc, argv):
    interface.call_function(ctx, _{{ fn.namespaced_name }}, argc, argv)

{% endfor %}
