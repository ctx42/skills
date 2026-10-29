---
type: regex
target: {source: file, path: initiatives/slot-swap/srd.md}
match: not_contains
flags: "m"
---
^## Requirements\b[\s\S]*^## Terms\b|^## Terms\b[\s\S]*^## (Introduction|Conventions|Boundaries)\b
