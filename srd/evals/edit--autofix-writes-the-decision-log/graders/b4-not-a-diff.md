---
type: regex
target: {source: file, path: specs/login.decisions.md}
match: not_contains
flags: "m"
---
^(\+|```|@@)
