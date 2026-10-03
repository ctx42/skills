---
type: regex
target: {source: file, path: tmp/csv-export-plan.md}
match: "not_contains"
flags: "m"
---
^## \d+\.(?![^\n]*— \[[ x]\])[^\n]*$
