---
type: regex
target: {source: file, path: specs/gateway.review.md}
flags: "m"
---
^- \[ \] #\d+ \[[a-z]+, reference[^\]]*\](?:(?!^- |^## |^---)[\s\S])*?GW-5\b
