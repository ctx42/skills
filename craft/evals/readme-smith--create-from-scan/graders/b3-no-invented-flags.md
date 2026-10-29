---
type: regex
target: {source: file, path: README.md}
match: "not_contains"
---
(^|[\s`])--?(verbose|retries|retry|format|output|quiet|ports?)\b
