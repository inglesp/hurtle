#include "sqlite3ext.h"
SQLITE_EXTENSION_INIT1

{% for fn in functions %}
{% include "function_decls.c.tpl" %}
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

{% for vtab in virtual_tables %}
{% include "virtual_table_decls.c.tpl" %}
{% endfor %}

int sqlite3_{{ extension_name}}_init(sqlite3 *db, char **pzErrMsg,
                            const sqlite3_api_routines *pApi) {
  int rc;
  SQLITE_EXTENSION_INIT2(pApi);

{% for fn in functions %}
{% include "function.c.tpl" %}
{% endfor %}

{% for vtab in virtual_tables %}
{% include "virtual_table.c.tpl" %}
{% endfor %}

  return SQLITE_OK;
}
