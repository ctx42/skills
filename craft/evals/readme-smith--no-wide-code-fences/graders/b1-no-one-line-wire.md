---
type: regex
target: {source: file, path: README.md}
match: "not_contains"
---
\\r\\n[^\n]*\\r\\n[^\n]*\\r\\n
