---
type: regex
target: {source: file, path: specs/api.review.md}
flags: "m"
---
^- \[ \] #\d+ \[blocker[^\]]*\](?:(?!^- |^## |^---)[\s\S])*?STR-3\b
