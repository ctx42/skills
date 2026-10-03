---
type: regex
target: {source: file, path: assets/flawed-srd.review.md}
flags: "m"
---
^- \[ \] #\d+ (?:(?!^- |^## |^---)[\s\S])*?GR-3\b(?:(?!^- |^## |^---)[\s\S])*?LANG-5\b
