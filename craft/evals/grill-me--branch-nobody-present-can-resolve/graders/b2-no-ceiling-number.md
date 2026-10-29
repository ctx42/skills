---
type: regex
target: {source: file, path: plans/rollout.md}
match: "not_contains"
flags: "i"
---
(ceiling|concurrency|\bcap\b)[^\n.]{0,40}\b\d+\s*(concurrent|jobs?|workers?|requests?|slots?|tasks?)\b
