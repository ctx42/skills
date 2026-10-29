---
type: regex
target: {source: file, path: initiatives/scrub-refunds/srd.review.md}
flags: "m"
---
^## Errata\n(?:(?!^## )[\s\S])*?^- \[ \] #2 (?:(?!^- |^## |^---)[\s\S])*?`wheather`(?:(?!^- |^## |^---)[\s\S])*?`weather`
