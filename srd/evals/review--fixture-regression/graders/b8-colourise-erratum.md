---
type: regex
target: {source: file, path: assets/flawed-srd.review.md}
flags: "m"
---
^## Errata\n(?:(?!^## )[\s\S])*?^- \[ \] #\d+ \[minor(?:(?!^- |^## |^---)[\s\S])*?colourise
