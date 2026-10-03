---
type: regex
target: {source: file, path: specs/login.review.md}
match: not_contains
flags: "m"
---
^- (?:\[[ x]\] )?#(\d+) [\s\S]*^- (?:\[[ x]\] )?#\1
