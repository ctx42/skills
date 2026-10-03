---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "m"
---
^- \[ \] #4 (?:(?!^- |^## |^---)[\s\S])*?`behaviour`\s*→\s*`behavior`
