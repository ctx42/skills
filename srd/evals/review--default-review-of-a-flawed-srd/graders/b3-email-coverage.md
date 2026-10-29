---
type: regex
target: {source: file, path: initiatives/scrub-refunds/srd.review.md}
flags: "m"
---
^- \[ \] #\d+ \[blocker, coverage[^\]]*\](?:(?!^- |^## |^---)[\s\S])*?[Ee]mail(?:(?!^- |^## |^---)[\s\S])*?\(SRD:BND-2\)
