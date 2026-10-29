---
type: regex
target: {source: file, path: initiatives/telemetry-replay/srd.review.md}
match: not_contains
flags: "mi"
---
^- \[ \] #\d+ (?=(?:(?!^- |^## |^---)[\s\S])*?TLM-6\b)(?:(?!^- |^## |^---)[\s\S])*?(authoritative|precedence|outrank|source of truth|\bwins\b|more trusted|leads on)
