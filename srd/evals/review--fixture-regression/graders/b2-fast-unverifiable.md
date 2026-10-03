---
type: regex
target: {source: file, path: assets/flawed-srd.review.md}
flags: "mi"
---
^- \[ \] #\d+ (?:(?!^- |^## |^---)[\s\S])*?fast(?:(?!^- |^## |^---)[\s\S])*?REQ-6\b
