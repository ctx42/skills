---
type: regex
target: {source: file, path: service_test.go}
match: not_contains
flags: "m"
---
^ +\S
