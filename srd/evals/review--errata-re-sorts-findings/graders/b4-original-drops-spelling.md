---
type: regex
target: {source: file, path: initiatives/scrub-refunds/srd.review.md}
match: not_contains
flags: "m"
---
^- \[ \] #4 (?:(?!^- |^## |^---)[\s\S])*?behaviou?r
