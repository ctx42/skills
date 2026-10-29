---
type: regex
target: {source: file, path: initiatives/telemetry-replay/srd.review.md}
match: not_contains
flags: "mi"
---
^- \[ \] #\d+ (?:(?!^- |^## |^---)[\s\S])*?TLM-2\b(?:(?!^- |^## |^---)[\s\S])*?(corpus|unconfirm|undocumented|documentation|cannot be confirmed)
