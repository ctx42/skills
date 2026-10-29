---
type: regex
target: {source: file, path: initiatives/scrub-refunds/srd.review.md}
flags: "m"
---
^- \[ \] #\d+ \[blocker, atomicity[^\]]*\](?:(?!^- |^## |^---)[\s\S])*?REF-4\b(?:(?!^- |^## |^---)[\s\S])*?\(SRD:RQT-1\)
