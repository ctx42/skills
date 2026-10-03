---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "m"
---
^- \[ \] #\d+ (?:(?!^- |^## |^---)[\s\S])*?GR-4\b(?:(?!^- |^## |^---)[\s\S])*?LANG-\d
