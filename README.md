# Myrtle

Myrtle will let you write [run-time loadable extensions for SQLite](https://sqlite.org/loadext.html) in Python.

It is a work in progress.


## Building and testing an extension

The following works with Python 3.7 on OSX.

* Run `gcc shell.c sqlite3.c -lpthread -ldl -o sqlite3` or equivalent (see [SQLite docs](https://sqlite.org/howtocompile.html#compiling_the_command_line_interface))
    * This will build a `sqlite3` binary
* Create and activate a Python 3.7 virtualenv, and run `pip install -r requirements.txt`
* Make a note of location of virtualenv's `site-packages` directory
* Run `CPATH=sqlite-amalgamation-3210000 python test.py`
    * This will create a DLL (`testplg.dll` on Windows, `testplg.dylib` on Mac OS/X, or `testplg.so` on other platforms)

Then:

```
$ PYTHONPATH=:/path/to/site-packages ./sqlite-amalgamation-3210000/sqlite3
SQLite version 3.21.0 2017-10-24 18:55:49
Enter ".help" for usage hints.
Connected to a transient in-memory database.
Use ".open FILENAME" to reopen on a persistent database.
sqlite> .load testplg
sqlite> select rot13('hello world');
uryyb jbeyq
sqlite> select product(1, 2, 3);
6
```


## Notes

* SQLite files come from https://sqlite.org/2017/sqlite-amalgamation-3210000.zip
* Setting `PYTHONPATH` is required, even if the virtualenv is activated -- I have no idea why
* I wrote most of this code a year ago, and don't currently understand it
