---
type: regex
target: {source: file, path: initiatives/scrub-refunds/srd.review.md}
flags: "m"
---
^## Requirements\n(?:(?!^## )[\s\S])*?^- \[ \] #4 (?:(?!^- |^## |^---)[\s\S])*?REF-5
