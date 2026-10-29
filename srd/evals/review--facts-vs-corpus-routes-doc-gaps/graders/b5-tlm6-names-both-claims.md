---
type: regex
target: {source: file, path: initiatives/telemetry-replay/srd.review.md}
flags: "m"
---
^- \[ \] #\d+ (?=(?:(?!^- |^## |^---)[\s\S])*?TLM-6\b)(?=(?:(?!^- |^## |^---)[\s\S])*?\b30\b)(?=(?:(?!^- |^## |^---)[\s\S])*?\b90\b)
