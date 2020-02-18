#include "sqlite3ext.h"
SQLITE_EXTENSION_INIT1

static int seriesConnect(sqlite3 *db, void *pAux, int argc,
                         const char *const *argv, sqlite3_vtab **ppVtab,
                         char **pzErr);
static int seriesDisconnect(sqlite3_vtab *pVtab);
static int seriesOpen(sqlite3_vtab *p, sqlite3_vtab_cursor **ppCursor);
static int seriesClose(sqlite3_vtab_cursor *cur);
static int seriesNext(sqlite3_vtab_cursor *cur);
static int seriesColumn(sqlite3_vtab_cursor *cur, sqlite3_context *ctx, int i);

static int seriesRowid(sqlite3_vtab_cursor *cur, sqlite_int64 *pRowid);
static int seriesEof(sqlite3_vtab_cursor *cur);
static int seriesFilter(sqlite3_vtab_cursor *pVtabCursor, int idxNum,
                        const char *idxStr, int argc, sqlite3_value **argv);
static int seriesBestIndex(sqlite3_vtab *tab, sqlite3_index_info *pIdxInfo);


/* series_cursor is a subclass of sqlite3_vtab_cursor which will
** serve as the underlying representation of a cursor that scans
** over rows of the result
*/
typedef struct series_cursor series_cursor;
struct series_cursor {
  sqlite3_vtab_cursor base;  /* Base class - must be first */
  int cursor_key;
};

static sqlite3_module seriesModule = {
  0,                         /* iVersion */
  0,                         /* xCreate */
  seriesConnect,             /* xConnect */
  seriesBestIndex,           /* xBestIndex */
  seriesDisconnect,          /* xDisconnect */
  0,                         /* xDestroy */
  seriesOpen,                /* xOpen - open a cursor */
  seriesClose,               /* xClose - close a cursor */
  seriesFilter,              /* xFilter - configure scan constraints */
  seriesNext,                /* xNext - advance a cursor */
  seriesEof,                 /* xEof - check for end of scan */
  seriesColumn,              /* xColumn - read data */
  seriesRowid,               /* xRowid - read data */
  0,                         /* xUpdate */
  0,                         /* xBegin */
  0,                         /* xSync */
  0,                         /* xCommit */
  0,                         /* xRollback */
  0,                         /* xFindMethod */
  0,                         /* xRename */
};


int sqlite3_seriespy_init(sqlite3 *db, char **pzErrMsg,
                        const sqlite3_api_routines *pApi) {
  SQLITE_EXTENSION_INIT2(pApi);
  return sqlite3_create_module(db, "generate_series", &seriesModule, 0);
}
