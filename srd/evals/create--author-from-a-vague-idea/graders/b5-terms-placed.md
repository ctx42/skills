---
type: regex
target: {source: file, path: initiatives/password-reset/srd.md}
match: not_contains
flags: "m"
---
^## Requirements\b[\s\S]*^## Terms\b|^## Terms\b[\s\S]*^## (Introduction|Conventions|Boundaries)\b
