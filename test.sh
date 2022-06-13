set -euo pipefail

VERSION=3380500
CPATH=sqlite-amalgamation-$VERSION python build_demo.py
echo "built!"
echo
echo
echo
PYTHONPATH=:~/.pyenv/versions/myrtle/lib/python3.10/site-packages ./sqlite-amalgamation-$VERSION/sqlite3 <test.sql
