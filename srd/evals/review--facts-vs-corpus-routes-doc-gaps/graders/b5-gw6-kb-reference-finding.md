---
type: regex
target: {source: file, path: specs/gateway.review.md}
flags: "m"
---
^- \[ \] #\d+ \[[a-z]+, reference[^\]]*\](?:(?!^- |^## |^---)[\s\S])*?GW-6\b(?:(?!^- |^## |^---)[\s\S])*?kb/api-gateway\.md
