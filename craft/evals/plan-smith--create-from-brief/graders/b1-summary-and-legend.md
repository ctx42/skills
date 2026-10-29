---
type: regex
target: {source: file, path: tmp/sso-plan.md}
flags: "m"
---
^# [^\n]+\n\n## Summary\n\n\| #[\s\S]*^Legend:[^\n]*Y[^\n]*implemented[^\n]*N[^\n]*not yet[^\n]*X[^\n]*rejected
