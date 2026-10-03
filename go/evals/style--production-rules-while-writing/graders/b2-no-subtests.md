---
type: regex
target: {source: file, path: service.go}
match: not_contains
---
t\.Run\(|\*testing\.T
