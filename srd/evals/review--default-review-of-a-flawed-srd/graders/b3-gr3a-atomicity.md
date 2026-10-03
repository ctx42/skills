---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "m"
---
^- \[ \] #\d+ \[blocker, atomicity[^\]]*\](?:(?!^- |^## |^---)[\s\S])*?GR-3a(?:(?!^- |^## |^---)[\s\S])*?\(SRD:REQ-1\)
