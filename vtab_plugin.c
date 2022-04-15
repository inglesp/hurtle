#include "sqlite3ext.h"
SQLITE_EXTENSION_INIT1

static int csvCreate(sqlite3 *db, void *pAux, int argc,
                     const char *const *argv, sqlite3_vtab **ppVtab,
                     char **pzErr);
static int csvConnect(sqlite3 *db, void *pAux, int argc,
                      const char *const *argv, sqlite3_vtab **ppVtab,
                      char **pzErr);
static int csvDisconnect(sqlite3_vtab *pVtab);
static int csvOpen(sqlite3_vtab *p, sqlite3_vtab_cursor **ppCursor);
static int csvClose(sqlite3_vtab_cursor *cur);
static int csvNext(sqlite3_vtab_cursor *cur);
static int csvColumn(sqlite3_vtab_cursor *cur, sqlite3_context *ctx, int i);

static int csvRowid(sqlite3_vtab_cursor *cur, sqlite_int64 *pRowid);
static int csvEof(sqlite3_vtab_cursor *cur);
static int csvFilter(sqlite3_vtab_cursor *pVtabCursor, int idxNum,
                        const char *idxStr, int argc, sqlite3_value **argv);
static int csvBestIndex(sqlite3_vtab *tab, sqlite3_index_info *pIdxInfo);


typedef struct csv_table csv_table;
struct csv_table {
  sqlite3_vtab base;  /* Base class - must be first */
  int table_key;
};

typedef struct csv_cursor csv_cursor;
struct csv_cursor {
  sqlite3_vtab_cursor base;  /* Base class - must be first */
  int cursor_key;
};

static sqlite3_module csvModule = {
  0,                      /* iVersion */
  csvCreate,              /* xCreate */
  csvConnect,             /* xConnect */
  csvBestIndex,           /* xBestIndex */
  csvDisconnect,          /* xDisconnect */
  csvDisconnect,          /* xDestroy */
  csvOpen,                /* xOpen - open a cursor */
  csvClose,               /* xClose - close a cursor */
  csvFilter,              /* xFilter - configure scan constraints */
  csvNext,                /* xNext - advance a cursor */
  csvEof,                 /* xEof - check for end of scan */
  csvColumn,              /* xColumn - read data */
  csvRowid,               /* xRowid - read data */
  0,                      /* xUpdate */
  0,                      /* xBegin */
  0,                      /* xSync */
  0,                      /* xCommit */
  0,                      /* xRollback */
  0,                      /* xFindMethod */
  0,                      /* xRename */
};


int sqlite3_csvpy_init(sqlite3 *db, char **pzErrMsg,
                        const sqlite3_api_routines *pApi) {
  SQLITE_EXTENSION_INIT2(pApi);
  return sqlite3_create_module(db, "csv", &csvModule, 0);
}
