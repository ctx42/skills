---
type: regex
target: {source: file, path: specs/gateway.review.md}
flags: "m"
---
^- \[ \] #\d+ (?=(?:(?!^- |^## |^---)[\s\S])*?GW-6\b)(?=(?:(?!^- |^## |^---)[\s\S])*?\b30\b)(?=(?:(?!^- |^## |^---)[\s\S])*?\b90\b)
