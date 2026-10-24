#!/bin/sh
# Project checks: script syntax, unit tests, and local links on every page.
set -eu
cd "$(dirname "$0")"
for f in *.js; do
    node --check "$f"
done
node --test tests/*.test.js
python3 -I tests/check_pages.py
