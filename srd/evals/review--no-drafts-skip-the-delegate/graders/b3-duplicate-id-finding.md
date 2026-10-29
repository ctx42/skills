---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "m"
---
^- \[ \] #\d+ (?:(?!^- |^## |^---)[\s\S])*?LCK-2\b(?:(?!^- |^## |^---)[\s\S])*?RQT-3\b
