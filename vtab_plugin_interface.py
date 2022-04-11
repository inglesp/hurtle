from csvpy import ffi

import vtab_plugin


@ffi.def_extern()
def csvCreate(db, pAux, argc, argv, ppVtab, pzErr):
    return vtab_plugin.connect(db, pAux, argc, argv, ppVtab, pzErr)


@ffi.def_extern()
def csvConnect(db, pAux, argc, argv, ppVtab, pzErr):
    return vtab_plugin.connect(db, pAux, argc, argv, ppVtab, pzErr)


@ffi.def_extern()
def csvDisconnect(pVtab):
    return vtab_plugin.disconnect(pVtab)


@ffi.def_extern()
def csvOpen(p, ppCursor):
    return vtab_plugin.open_(p, ppCursor)


@ffi.def_extern()
def csvClose(cur):
    return vtab_plugin.close_(cur)


@ffi.def_extern()
def csvNext(cur):
    return vtab_plugin.next_(cur)


@ffi.def_extern()
def csvColumn(cur, ctx, i):
    return vtab_plugin.column(cur, ctx, i)


@ffi.def_extern()
def csvRowid(cur, pRowid):
    return vtab_plugin.row_id(cur, pRowid)


@ffi.def_extern()
def csvEof(cur):
    return vtab_plugin.eof(cur)


@ffi.def_extern()
def csvFilter(pVtabCursor, idxNum, idxStr, argc, argv):
    return vtab_plugin.filter_(pVtabCursor, idxNum, idxStr, argc, argv)


@ffi.def_extern()
def csvBestIndex(tab, pIdxInfo):
    return vtab_plugin.best_index(tab, pIdxInfo)
