---
type: regex
target: {source: file, path: initiatives/telemetry-replay/srd.review.md}
flags: "m"
---
^- \[ \] #\d+ \[[a-z]+, reference[^\]]*\](?:(?!^- |^## |^---)[\s\S])*?TLM-5\b
