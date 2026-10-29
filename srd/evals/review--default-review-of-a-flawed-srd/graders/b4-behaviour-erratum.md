---
type: regex
target: {source: file, path: initiatives/scrub-refunds/srd.review.md}
flags: "m"
---
^## Errata\n(?:(?!^## )[\s\S])*?^- \[ \] #\d+ \[minor, linguistic\](?:(?!^- |^## |^---)[\s\S])*?`behaviour`\s*→\s*`behavior`(?:(?!^- |^## |^---)[\s\S])*?\(SRD:house\)
