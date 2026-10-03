---
type: regex
target: {source: file, path: pkg/svc/foo_test.go}
match: not_contains
---
\bif\s+!?(tc|tt|test)\.\w+
