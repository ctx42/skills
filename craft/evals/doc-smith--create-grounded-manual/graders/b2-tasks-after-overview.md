---
type: regex
target: {source: file, path: docs/user-manual.md}
flags: "im"
---
^#[^#\n][^\n]*\n\s*(?:[^#\s][^\n]*\n|## [^\n]*(?:overview|about|introduction|what)[^\n]*\n)[\s\S]*^#{2,3} [^\n]*\b(pay|paying)\b
