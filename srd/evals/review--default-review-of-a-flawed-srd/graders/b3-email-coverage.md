---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "m"
---
^- \[ \] #\d+ \[blocker, coverage[^\]]*\](?:(?!^- |^## |^---)[\s\S])*?[Ee]mail(?:(?!^- |^## |^---)[\s\S])*?\(SRD:BND-2\)
