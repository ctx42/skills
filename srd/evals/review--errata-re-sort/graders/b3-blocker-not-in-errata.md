---
type: regex
target: {source: file, path: specs/login.review.md}
match: not_contains
flags: "m"
---
^## Errata\n(?:(?!^## )[\s\S])*?#2
