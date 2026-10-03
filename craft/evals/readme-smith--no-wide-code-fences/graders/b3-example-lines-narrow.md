---
type: regex
target: {source: file, path: example_test.go}
match: "not_contains"
flags: "m"
---
^[^\n]{101,}$
