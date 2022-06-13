# Hurtle: Run-Time Loadable Extensions (for Humans)

Hurtle will let you write [run-time loadable extensions for SQLite](https://sqlite.org/loadext.html) in Python.

It is a work in progress.

The following works with Python 3.10 on Ubuntu.

* Build a `sqlite3` binary: 
    * `cd sqlite-amalgamation-3380500/ && gcc shell.c sqlite3.c -lpthread -ldl -o sqlite3` or equivalent (see [SQLite docs](https://sqlite.org/howtocompile.html#compiling_the_command_line_interface))
* Then run `./test.sh` to try out the demos
