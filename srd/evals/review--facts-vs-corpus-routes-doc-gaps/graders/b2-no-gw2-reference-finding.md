---
type: regex
target: {source: file, path: specs/gateway.review.md}
match: not_contains
flags: "m"
---
^- \[ \] #\d+ \[[a-z]+, reference[^\]]*\](?:(?!^- |^## |^---)[\s\S])*?GW-2\b
