---
type: regex
target: {source: file, path: initiatives/telemetry-replay/srd.review.md}
match: not_contains
flags: "m"
---
^- \[ \] #\d+ \[[a-z]+, reference[^\]]*\](?:(?!^- |^## |^---)[\s\S])*?TLM-2\b
