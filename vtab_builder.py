import cffi

ffibuilder = cffi.FFI()
ffibuilder.embedding_api(open('vtab_plugin_api.h').read())
ffibuilder.embedding_init_code(open('vtab_plugin_interface.py').read())
ffibuilder.set_source('seriespy', open('vtab_plugin.c').read())
ffibuilder.compile()
