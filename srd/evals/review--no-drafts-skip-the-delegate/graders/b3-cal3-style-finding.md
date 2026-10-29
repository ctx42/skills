---
type: regex
target: {source: file, path: initiatives/bay-calendar/srd.review.md}
flags: "m"
---
^- \[ \] #\d+ (?:(?!^- |^## |^---)[\s\S])*?CAL-3\b(?:(?!^- |^## |^---)[\s\S])*?CLR-\d
