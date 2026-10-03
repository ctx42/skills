---
type: regex
target: {source: file, path: assets/flawed-srd.review.md}
flags: "m"
---
^- \[ \] #\d+ (?:(?!^- |^## |^---)[\s\S])*?GR-4\b(?:(?!^- |^## |^---)[\s\S])*?SCO-3\b
