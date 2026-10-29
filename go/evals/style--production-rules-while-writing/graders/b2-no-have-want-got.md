---
type: regex
target: {source: file, path: service.go}
match: not_contains
---
\b(have|want|got)\b
