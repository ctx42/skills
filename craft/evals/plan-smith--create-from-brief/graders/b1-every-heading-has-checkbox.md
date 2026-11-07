---
type: regex
target: {source: file, path: tmp/agent-plan-sso.md}
match: "not_contains"
flags: "m"
---
^## \d+\.(?![^\n]*— \[[ x]\])[^\n]*$
