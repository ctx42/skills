---
type: regex
target: {source: file, path: docs/user-manual.md}
match: "not_contains"
flags: "i"
---
(?<![/\w`])bills?\b
