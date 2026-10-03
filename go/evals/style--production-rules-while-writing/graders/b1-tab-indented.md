---
type: regex
target: {source: file, path: service.go}
match: not_contains
flags: "m"
---
^ +\S
