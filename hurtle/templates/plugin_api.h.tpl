{% include "sqlite3.h" %}

{% for fn in functions %}
{% include "function.h.tpl" %}
{% endfor %}

{% if virtual_tables %}
typedef struct __hurtle_table __hurtle_table;
struct __hurtle_table {
  sqlite3_vtab base;
  int table_key;
};

typedef struct __hurtle_cursor __hurtle_cursor;
struct __hurtle_cursor {
  sqlite3_vtab_cursor base;
  int cursor_key;
};
{% endif %}

{% for virtual_table in virtual_tables %}
{% with namespaced_name=virtual_table.namespaced_name, path=virtual_table.path %}
{% include "virtual_table.h.tpl" %}
{% endwith %}
{% endfor %}
