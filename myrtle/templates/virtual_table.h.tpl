static int {{ namespaced_name }}Create(sqlite3 *db, void *pAux, int argc,
                         const char *const *argv, sqlite3_vtab **ppVtab,
                         char **pzErr);
static int {{ namespaced_name }}Connect(sqlite3 *db, void *pAux, int argc,
                         const char *const *argv, sqlite3_vtab **ppVtab,
                         char **pzErr);
static int {{ namespaced_name }}Disconnect(sqlite3_vtab *pVtab);
static int {{ namespaced_name }}Open(sqlite3_vtab *p, sqlite3_vtab_cursor **ppCursor);
static int {{ namespaced_name }}Close(sqlite3_vtab_cursor *cur);
static int {{ namespaced_name }}Next(sqlite3_vtab_cursor *cur);
static int {{ namespaced_name }}Column(sqlite3_vtab_cursor *cur, sqlite3_context *ctx, int i);
static int {{ namespaced_name }}Rowid(sqlite3_vtab_cursor *cur, sqlite_int64 *pRowid);
static int {{ namespaced_name }}Eof(sqlite3_vtab_cursor *cur);
static int {{ namespaced_name }}Filter(sqlite3_vtab_cursor *pVtabCursor, int idxNum,
                        const char *idxStr, int argc, sqlite3_value **argv);
static int {{ namespaced_name }}BestIndex(sqlite3_vtab *tab, sqlite3_index_info *pIdxInfo);

typedef struct {{ namespaced_name }}_table {{ namespaced_name }}_table;
struct {{ namespaced_name }}_table {
  sqlite3_vtab base;
  int table_key;
};

typedef struct {{ namespaced_name }}_cursor {{ namespaced_name }}_cursor;
struct {{ namespaced_name }}_cursor {
  sqlite3_vtab_cursor base;
  int cursor_key;
};
