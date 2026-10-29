---
type: regex
target: {source: file, path: docs/guide.md}
match: "not_contains"
flags: "im"
---
^#{1,3}\s[^\n]*\bproject
