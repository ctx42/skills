---
type: regex
target: {source: file, path: initiatives/scrub-refunds/srd.review.md}
flags: "m"
---
^## Errata\n(?:(?!^## )[\s\S])*?^- \[ \] #1 (?:(?!^- |^## |^---)[\s\S])*?`amout`(?:(?!^- |^## |^---)[\s\S])*?`amount`
