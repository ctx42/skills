---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "m"
---
^## Requirements\n(?:(?!^## )[\s\S])*?^- \[ \] #4 (?:(?!^- |^## |^---)[\s\S])*?GR-5
