---
type: regex
target: {source: file, path: docs/user-manual.md}
flags: "im"
---
^#[^#\n][^\n]*\n(?:(?!^## )[\s\S])*?^## [^\n]*(overview|about|introduction|what)
