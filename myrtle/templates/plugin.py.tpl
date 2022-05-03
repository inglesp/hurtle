from myrtle.import_helpers import import_attr
from myrtle.interface import Interface

from {{ extension_name }} import ffi, lib

interface = Interface(ffi, lib)

{% for fn in functions %}
{% include "function.py.tpl" %}
{% endfor %}
