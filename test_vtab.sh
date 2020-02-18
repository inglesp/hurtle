set -e

CPATH=sqlite-amalgamation-3210000 python vtab_builder.py
PYTHONPATH=:~/.pyenv/versions/chortle/lib/python3.8/site-packages ./sqlite-amalgamation-3210000/sqlite3 <<EOF
.load seriespy
select * from generate_series(0, 6, 2);
EOF
