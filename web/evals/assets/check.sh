#!/bin/sh
# Project checks: script syntax, unit tests, and the server's syntax.
set -eu
cd "$(dirname "$0")"
for f in *.js tests/*.js; do
    node --check "$f"
done
node --test tests/*.test.js
python3 -I -c 'import ast, sys; ast.parse(open(sys.argv[1]).read())' server.py
