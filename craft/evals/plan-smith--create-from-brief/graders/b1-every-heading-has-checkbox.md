---
type: regex
target: {source: file, path: tmp/sso-plan.md}
match: "not_contains"
flags: "m"
---
^## \d+\.(?![^\n]*— \[[ x]\])[^\n]*$
