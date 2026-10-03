---
type: regex
target: {source: file, path: specs/gateway.review.md}
match: not_contains
flags: "mi"
---
^- \[ \] #\d+ (?:(?!^- |^## |^---)[\s\S])*?GW-2\b(?:(?!^- |^## |^---)[\s\S])*?(corpus|unconfirm|undocumented|documentation|cannot be confirmed)
