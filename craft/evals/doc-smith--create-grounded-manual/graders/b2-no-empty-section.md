---
type: regex
target: {source: file, path: docs/user-manual.md}
match: "not_contains"
flags: "im"
---
^## [^\n]+\n\s*## |\b(TBD|TODO|coming soon)\b
