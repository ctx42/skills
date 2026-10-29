---
type: regex
target: {source: file, path: initiatives/bay-calendar/srd.review.md}
flags: "m"
---
^- \[ \] #\d+ (?:(?!^- |^## |^---)[\s\S])*?CAL-4\b(?:(?!^- |^## |^---)[\s\S])*?CLR-\d
