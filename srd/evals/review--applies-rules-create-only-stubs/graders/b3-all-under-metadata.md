---
type: regex
target: {source: file, path: specs/api.review.md}
flags: "m"
---
^## Metadata\n(?=(?:(?!^## )[\s\S])*STR-2\b)(?=(?:(?!^## )[\s\S])*STR-3\b)(?=(?:(?!^## )[\s\S])*STA-2\b)
