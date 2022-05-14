from myrtle.import_helpers import import_attr
from myrtle.interface import Interface

from {{ extension_name }} import ffi, lib

interface = Interface(ffi, lib)

{% for fn in functions %}
{% include "function.py.tpl" %}
{% endfor %}

{% for virtual_table in virtual_tables %}
{% with namespaced_name=virtual_table.namespaced_name, path=virtual_table.path %}
{% include "virtual_table.py.tpl" %}
{% endwith %}
{% endfor %}
