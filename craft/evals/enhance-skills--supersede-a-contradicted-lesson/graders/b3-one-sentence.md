---
type: regex
target: {source: file, path: craft/skills/plan-smith/LESSONS.md}
match: "not_contains"
flags: "m"
---
^- (?=(?:[^\n]|\n  )*docs/plans)(?:[^\n]|\n  )*?(\.\s+\S|;)
