---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "m"
---
^- \[ \] #\d+ \[blocker, coverage[^\]]*\](?:(?!^- |^## |^---)[\s\S])*?SC-2(?:(?!^- |^## |^---)[\s\S])*?\(SRD:SCO-2\)
