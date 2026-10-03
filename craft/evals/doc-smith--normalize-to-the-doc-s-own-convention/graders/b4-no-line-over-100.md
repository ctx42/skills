---
type: regex
target: {source: file, path: docs/guide.md}
match: "not_contains"
flags: "m"
---
^(?![|#])[^\n]{101,}$
