---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "m"
---
^- \[ \] #\d+ (?:(?!^- |^## |^---)[\s\S])*?GR-3\b(?:(?!^- |^## |^---)[\s\S])*?LANG-\d
