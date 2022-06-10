{% include "sqlite3.h" %}

{% for fn in functions %}
{% include "function.h.tpl" %}
{% endfor %}

{% if virtual_tables %}
typedef struct __myrtle_table __myrtle_table;
struct __myrtle_table {
  sqlite3_vtab base;
  int table_key;
};

typedef struct __myrtle_cursor __myrtle_cursor;
struct __myrtle_cursor {
  sqlite3_vtab_cursor base;
  int cursor_key;
};
{% endif %}

{% for virtual_table in virtual_tables %}
{% with namespaced_name=virtual_table.namespaced_name, path=virtual_table.path %}
{% include "virtual_table.h.tpl" %}
{% endwith %}
{% endfor %}
