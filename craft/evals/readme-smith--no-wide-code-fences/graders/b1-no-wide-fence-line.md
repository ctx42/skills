---
type: regex
target: {source: file, path: README.md}
match: "not_contains"
---
(^|\n)```[a-z]*\n(?:(?!```)[^\n]*\n)*?(?!```)[^\n]{101,}\n
