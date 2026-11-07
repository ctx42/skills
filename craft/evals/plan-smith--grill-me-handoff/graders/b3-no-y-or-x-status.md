---
type: regex
target: {source: file, path: tmp/agent-plan-csv-export.md}
match: "not_contains"
flags: "m"
---
^\|[^|\n]*\|[^|\n]*\| *[YX] *\|$
