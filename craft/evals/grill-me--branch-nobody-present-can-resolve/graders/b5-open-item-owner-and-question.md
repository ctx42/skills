---
type: regex
target: {source: file, path: plans/rollout.md}
flags: "im"
---
^#{2,3} [^\n]*(platform team[^\n]*(concurrency|ceiling)|(concurrency|ceiling)[^\n]*platform team)
