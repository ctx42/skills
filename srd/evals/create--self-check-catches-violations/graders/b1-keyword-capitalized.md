---
type: regex
target: {source: file, path: initiatives/scheduled-export/srd.md}
match: not_contains
flags: "m"
---
^## Requirements\b(?:(?!^## )[\s\S])*?\bmust\b
