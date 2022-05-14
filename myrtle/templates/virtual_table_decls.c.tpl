static int {{ vtab.namespaced_name }}Create(sqlite3 *db, void *pAux, int argc,
                     const char *const *argv, sqlite3_vtab **ppVtab,
                     char **pzErr);
static int {{ vtab.namespaced_name }}Connect(sqlite3 *db, void *pAux, int argc,
                      const char *const *argv, sqlite3_vtab **ppVtab,
                      char **pzErr);
static int {{ vtab.namespaced_name }}Disconnect(sqlite3_vtab *pVtab);
static int {{ vtab.namespaced_name }}Open(sqlite3_vtab *p, sqlite3_vtab_cursor **ppCursor);
static int {{ vtab.namespaced_name }}Close(sqlite3_vtab_cursor *cur);
static int {{ vtab.namespaced_name }}Next(sqlite3_vtab_cursor *cur);
static int {{ vtab.namespaced_name }}Column(sqlite3_vtab_cursor *cur, sqlite3_context *ctx, int i);

static int {{ vtab.namespaced_name }}Rowid(sqlite3_vtab_cursor *cur, sqlite_int64 *pRowid);
static int {{ vtab.namespaced_name }}Eof(sqlite3_vtab_cursor *cur);
static int {{ vtab.namespaced_name }}Filter(sqlite3_vtab_cursor *pVtabCursor, int idxNum,
                        const char *idxStr, int argc, sqlite3_value **argv);
static int {{ vtab.namespaced_name }}BestIndex(sqlite3_vtab *tab, sqlite3_index_info *pIdxInfo);

typedef struct {{ vtab.namespaced_name }}_table {{ vtab.namespaced_name }}_table;
struct {{ vtab.namespaced_name }}_table {
  sqlite3_vtab base;
  int table_key;
};

typedef struct {{ vtab.namespaced_name }}_cursor {{ vtab.namespaced_name }}_cursor;
struct {{ vtab.namespaced_name }}_cursor {
  sqlite3_vtab_cursor base;
  int cursor_key;
};

static sqlite3_module {{ vtab.namespaced_name }}Module = {
  0,                                    /* iVersion */
  {{ vtab.namespaced_name }}Create,     /* xCreate */
  {{ vtab.namespaced_name }}Connect,    /* xConnect */
  {{ vtab.namespaced_name }}BestIndex,  /* xBestIndex */
  {{ vtab.namespaced_name }}Disconnect, /* xDisconnect */
  {{ vtab.namespaced_name }}Disconnect, /* xDestroy */
  {{ vtab.namespaced_name }}Open,       /* xOpen */
  {{ vtab.namespaced_name }}Close,      /* xClose */
  {{ vtab.namespaced_name }}Filter,     /* xFilter */
  {{ vtab.namespaced_name }}Next,       /* xNext */
  {{ vtab.namespaced_name }}Eof,        /* xEof */
  {{ vtab.namespaced_name }}Column,     /* xColumn */
  {{ vtab.namespaced_name }}Rowid,      /* xRowid */
  0,                                    /* xUpdate */
  0,                                    /* xBegin */
  0,                                    /* xSync */
  0,                                    /* xCommit */
  0,                                    /* xRollback */
  0,                                    /* xFindMethod */
  0,                                    /* xRename */
};
