---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "m"
---
^## Requirements\n(?:(?!^## )[\s\S])*?^- \[ \] #3 \[blocker, atomicity\] LCK-4:
