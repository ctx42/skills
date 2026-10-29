---
type: regex
target: {source: file, path: initiatives/scrub-refunds/srd.review.md}
flags: "m"
---
^## Errata\n(?:(?!^## )[\s\S])*?^- \[ \] #6 (?:(?!^- |^## |^---)[\s\S])*?`behaviour`(?:(?!^- |^## |^---)[\s\S])*?`behavior`
