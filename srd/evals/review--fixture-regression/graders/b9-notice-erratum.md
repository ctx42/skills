---
type: regex
target: {source: file, path: assets/flawed-srd.review.md}
flags: "m"
---
^## Errata\n(?:(?!^## )[\s\S])*?^- \[ \] #\d+ (?=(?:(?!^- |^## |^---)[\s\S])*?STR-8\b)(?:(?!^- |^## |^---)[\s\S])*?\[!INFO\](?:(?!^- |^## |^---)[\s\S])*?RFC 8174(?:(?!^- |^## |^---)[\s\S])*?\[!INFO\](?:(?!^- |^## |^---)[\s\S])*?RFC 2119
