  rc = sqlite3_create_module(db, "{{ vtab.name }}", &{{ vtab.namespaced_name }}Module, 0);
  if (rc != SQLITE_OK) {
    return rc;
  }
