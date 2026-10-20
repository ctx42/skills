---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "m"
---
^## Errata\n(?:(?!^## )[\s\S])*?^- \[ \] #2 (?:(?!^- |^## |^---)[\s\S])*?`succesful`(?:(?!^- |^## |^---)[\s\S])*?`successful`
