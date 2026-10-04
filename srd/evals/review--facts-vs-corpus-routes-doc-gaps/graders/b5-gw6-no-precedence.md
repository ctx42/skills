---
type: regex
target: {source: file, path: specs/gateway.review.md}
match: not_contains
flags: "mi"
---
^- \[ \] #\d+ (?=(?:(?!^- |^## |^---)[\s\S])*?GW-6\b)(?:(?!^- |^## |^---)[\s\S])*?(authoritative|precedence|outrank|source of truth|\bwins\b|more trusted|leads on)
