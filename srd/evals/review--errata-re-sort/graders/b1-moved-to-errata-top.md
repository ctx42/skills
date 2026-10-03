---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "m"
---
^# SRD Review[^\n]*\n+## Errata\n+- \[ \] #4 \[minor, linguistic\](?:(?!^- |^## |^---)[\s\S])*?\(SRD:house\)
