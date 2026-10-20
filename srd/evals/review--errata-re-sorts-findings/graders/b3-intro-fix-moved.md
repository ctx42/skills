---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "m"
---
^## Errata\n(?:(?!^## )[\s\S])*?^- \[ \] #1 (?:(?!^- |^## |^---)[\s\S])*?`attemps`(?:(?!^- |^## |^---)[\s\S])*?`attempts`
