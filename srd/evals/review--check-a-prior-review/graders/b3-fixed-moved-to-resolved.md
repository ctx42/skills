---
type: regex
target: {source: file, path: specs/login.review.md}
flags: "m"
---
^## Resolved\n(?=(?:(?!^## )[\s\S])*^- \[x\] #1 )(?=(?:(?!^## )[\s\S])*^- \[x\] #2 )
