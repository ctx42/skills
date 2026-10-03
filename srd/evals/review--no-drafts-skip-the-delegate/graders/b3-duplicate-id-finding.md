---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "m"
---
^- \[ \] #\d+ (?:(?!^- |^## |^---)[\s\S])*?GR-2\b(?:(?!^- |^## |^---)[\s\S])*?REQ-3\b
