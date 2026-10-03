---
type: regex
target: {source: file, path: specs/api.review.md}
flags: "m"
---
^- \[ \] #\d+ \[blocker[^\]]*\](?:(?!^- |^## |^---)[\s\S])*?STA-2\b
