---
type: regex
target: {source: file, path: tmp/agent/agent-plan-sso.md}
match: "not_contains"
flags: "m"
---
^## \d+\.(?![^\n]*— \[[ x]\])[^\n]*$
