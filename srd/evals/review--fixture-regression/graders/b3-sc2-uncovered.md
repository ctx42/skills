---
type: regex
target: {source: file, path: assets/flawed-srd.review.md}
flags: "m"
---
^- \[ \] #\d+ (?:(?!^- |^## |^---)[\s\S])*?SC-2\b(?:(?!^- |^## |^---)[\s\S])*?SCO-2\b
