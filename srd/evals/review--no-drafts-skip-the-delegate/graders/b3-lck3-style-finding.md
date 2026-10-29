---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "m"
---
^- \[ \] #\d+ (?:(?!^- |^## |^---)[\s\S])*?LCK-3\b(?:(?!^- |^## |^---)[\s\S])*?CLR-\d
