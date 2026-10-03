---
type: regex
target: {source: file, path: tmp/sso-plan.md}
match: "not_contains"
flags: "im"
---
^## \d+\.[^\n]*\b(tests?|testing|CI|monitor\w*|rollout|roll-out|migrat\w*|metrics|alert\w*)\b
