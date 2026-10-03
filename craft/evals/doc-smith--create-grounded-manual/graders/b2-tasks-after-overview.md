---
type: regex
target: {source: file, path: docs/user-manual.md}
flags: "im"
---
^## [^\n]*(overview|about|introduction)[\s\S]*^#{2,3} [^\n]*\b(pay|paying)\b
