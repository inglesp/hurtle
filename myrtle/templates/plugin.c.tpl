#include "sqlite3ext.h"
SQLITE_EXTENSION_INIT1

{% for fn in functions %}
{% include "function_decls.c.tpl" %}
{% endfor %}

int sqlite3_{{ extension_name}}_init(sqlite3 *db, char **pzErrMsg,
                            const sqlite3_api_routines *pApi) {
  int rc;
  SQLITE_EXTENSION_INIT2(pApi);

{% for fn in functions %}
{% include "function.c.tpl" %}
{% endfor %}

  return SQLITE_OK;
}
