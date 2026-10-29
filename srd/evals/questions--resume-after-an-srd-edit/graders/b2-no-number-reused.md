---
type: regex
target: {source: file, path: initiatives/part-kit-tracking/srd.review.md}
match: not_contains
flags: "m"
---
^- (?:\[[ x]\] )?#(\d+) [\s\S]*^- (?:\[[ x]\] )?#\1 
