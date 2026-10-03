---
type: regex
target: {source: file, path: craft/skills/plan-smith/LESSONS.md}
match: "count:1"
flags: "mi"
---
^- [^\n]*(\n  [^\n]*)*(path|docs/plans|tmp)
