---
type: regex
target: {source: file, path: specs/login.review.md}
match: not_contains
flags: "m"
---
^- \[ \] #4 (?:(?!^- |^## |^---)[\s\S])*?behaviou?r
