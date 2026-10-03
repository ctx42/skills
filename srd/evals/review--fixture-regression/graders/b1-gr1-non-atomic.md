---
type: regex
target: {source: file, path: assets/flawed-srd.review.md}
flags: "m"
---
^- \[ \] #\d+ (?:(?!^- |^## |^---)[\s\S])*?GR-1\b(?:(?!^- |^## |^---)[\s\S])*?REQ-1\b
