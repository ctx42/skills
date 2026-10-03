---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "mi"
---
^## Withdrawn\n(?:(?!^## )[\s\S])*^- #5 (?:(?!^- |^## |^---)[\s\S])*?withdrawn
