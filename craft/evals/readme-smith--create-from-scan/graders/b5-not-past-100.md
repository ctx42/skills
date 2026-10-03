---
type: regex
target: {source: file, path: README.md}
match: "not_contains"
flags: "m"
---
^[A-Za-z`*][^\n]{100,}$
