_{{ namespaced_name }} = interface.build_virtual_table(import_attr("{{ path }}"))


@ffi.def_extern()
def {{ namespaced_name }}Create(db, pAux, argc, argv, ppVtab, pzErr):
    return _{{ namespaced_name }}.connect(db, pAux, argc, argv, ppVtab, pzErr)


@ffi.def_extern()
def {{ namespaced_name }}Connect(db, pAux, argc, argv, ppVtab, pzErr):
    return _{{ namespaced_name }}.connect(db, pAux, argc, argv, ppVtab, pzErr)


@ffi.def_extern()
def {{ namespaced_name }}Disconnect(pVtab):
    return _{{ namespaced_name }}.disconnect(pVtab)


@ffi.def_extern()
def {{ namespaced_name }}Open(p, ppCursor):
    return _{{ namespaced_name }}.open_(p, ppCursor)


@ffi.def_extern()
def {{ namespaced_name }}Close(cur):
    return _{{ namespaced_name }}.close_(cur)


@ffi.def_extern()
def {{ namespaced_name }}Next(cur):
    return _{{ namespaced_name }}.next_(cur)


@ffi.def_extern()
def {{ namespaced_name }}Column(cur, ctx, i):
    return _{{ namespaced_name }}.column(cur, ctx, i)


@ffi.def_extern()
def {{ namespaced_name }}Rowid(cur, pRowid):
    return _{{ namespaced_name }}.row_id(cur, pRowid)


@ffi.def_extern()
def {{ namespaced_name }}Eof(cur):
    return _{{ namespaced_name }}.eof(cur)


@ffi.def_extern()
def {{ namespaced_name }}Filter(pVtabCursor, idxNum, idxStr, argc, argv):
    return _{{ namespaced_name }}.filter_(pVtabCursor, idxNum, idxStr, argc, argv)


@ffi.def_extern()
def {{ namespaced_name }}BestIndex(tab, pIdxInfo):
    return _{{ namespaced_name }}.best_index(tab, pIdxInfo)


