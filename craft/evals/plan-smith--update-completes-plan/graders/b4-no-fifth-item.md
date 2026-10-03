---
type: regex
target: {source: file, path: tmp/done-plan.md}
match: "not_contains"
flags: "m"
---
^## 5\.|^\| 5 
