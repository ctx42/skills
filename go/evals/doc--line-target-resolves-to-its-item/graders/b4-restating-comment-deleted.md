---
type: regex
target: {source: file, path: pkg/svc/foo.go}
match: "not_contains"
flags: "i"
---
//\s*(increment|incr|add one to|bump)\b[^\n]*\bi\b
