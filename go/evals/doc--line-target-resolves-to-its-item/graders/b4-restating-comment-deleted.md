---
type: regex
target: {source: file, path: pkg/svc/foo.go}
match: "not_contains"
---
//[^\n]*\n\t+i\+\+|increment i
