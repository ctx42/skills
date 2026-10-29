---
type: regex
target: {source: file, path: initiatives/bay-calendar/srd.review.md}
flags: "m"
---
^- \[ \] #\d+ (?:(?!^- |^## |^---)[\s\S])*?CAL-2\b(?:(?!^- |^## |^---)[\s\S])*?RQT-3\b
