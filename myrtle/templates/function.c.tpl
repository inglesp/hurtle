rc = sqlite3_create_function(db, "{{ fn.name }}", {{ fn.num_args }}, SQLITE_UTF8, 0, {{ fn.namespaced_name }}, 0, 0);
  if (rc != SQLITE_OK) {
    return rc;
  }

