---
type: regex
target: {source: file, path: tmp/agent/agent-plan-sso.md}
match: "not_contains"
flags: "im"
---
^## \d+\.[^\n]*\b(tests?|testing|CI|monitor\w*|rollout|roll-out|migrat\w*|metrics|alert\w*)\b
