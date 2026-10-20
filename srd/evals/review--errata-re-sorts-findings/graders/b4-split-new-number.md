---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "m"
---
^## Errata\n(?:(?!^## )[\s\S])*?^- \[ \] #6 (?:(?!^- |^## |^---)[\s\S])*?`behaviour`(?:(?!^- |^## |^---)[\s\S])*?`behavior`
