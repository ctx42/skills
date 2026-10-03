---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "m"
---
^- \[ \] #\d+ (?:(?!^- |^## |^---)[\s\S])*?STR-2\b
