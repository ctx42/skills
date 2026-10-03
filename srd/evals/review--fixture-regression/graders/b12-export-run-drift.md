---
type: regex
target: {source: file, path: assets/flawed-srd.review.md}
flags: "mi"
---
^- \[ \] #\d+ \[[^\]]*terminology[^\]]*\](?:(?!^- |^## |^---)[\s\S])*?export run
