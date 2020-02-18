from seriespy import ffi

import vtab_plugin


@ffi.def_extern()
def seriesConnect(db, pAux, argc, argv, ppVtab, pzErr):
    return vtab_plugin.connect(db, pAux, argc, argv, ppVtab, pzErr)


@ffi.def_extern()
def seriesDisconnect(pVtab):
    return vtab_plugin.disconnect(pVtab)


@ffi.def_extern()
def seriesOpen(p, ppCursor):
    return vtab_plugin.open_(p, ppCursor)


@ffi.def_extern()
def seriesClose(cur):
    return vtab_plugin.close_(cur)


@ffi.def_extern()
def seriesNext(cur):
    return vtab_plugin.next_(cur)


@ffi.def_extern()
def seriesColumn(cur, ctx, i):
    return vtab_plugin.column(cur, ctx, i)


@ffi.def_extern()
def seriesRowid(cur, pRowid):
    return vtab_plugin.row_id(cur, pRowid)


@ffi.def_extern()
def seriesEof(cur):
    return vtab_plugin.eof(cur)


@ffi.def_extern()
def seriesFilter(pVtabCursor, idxNum, idxStr, argc, argv):
    return vtab_plugin.filter_(pVtabCursor, idxNum, idxStr, argc, argv)


@ffi.def_extern()
def seriesBestIndex(tab, pIdxInfo):
    return vtab_plugin.best_index(tab, pIdxInfo)
