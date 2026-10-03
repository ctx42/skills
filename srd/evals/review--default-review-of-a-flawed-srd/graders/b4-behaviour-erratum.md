---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "m"
---
^## Errata\n(?:(?!^## )[\s\S])*?^- \[ \] #\d+ \[minor, linguistic\](?:(?!^- |^## |^---)[\s\S])*?`behaviour`\s*→\s*`behavior`(?:(?!^- |^## |^---)[\s\S])*?\(SRD:house\)
