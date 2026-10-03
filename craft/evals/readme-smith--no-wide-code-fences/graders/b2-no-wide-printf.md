---
type: regex
target: {source: file, path: example_test.go}
match: "not_contains"
---
Printf\("%q\\n", wire\)
