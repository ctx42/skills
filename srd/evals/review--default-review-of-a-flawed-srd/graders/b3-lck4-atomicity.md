---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "m"
---
^- \[ \] #\d+ \[blocker, atomicity[^\]]*\](?:(?!^- |^## |^---)[\s\S])*?LCK-4\b(?:(?!^- |^## |^---)[\s\S])*?\(SRD:RQT-1\)
