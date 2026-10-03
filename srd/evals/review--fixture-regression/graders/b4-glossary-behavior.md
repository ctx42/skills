---
type: regex
target: {source: file, path: assets/flawed-srd.review.md}
flags: "mi"
---
^- \[ \] #\d+ (?:(?!^- |^## |^---)[\s\S])*?Export Job(?:(?!^- |^## |^---)[\s\S])*?GLO-[12]\b
