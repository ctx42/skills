---
type: regex
target: {source: file, path: README.md}
match: "not_contains"
---
^(?=[\s\S]*<!-- TOC -->)(?=[\s\S]*\]\(#[\w-]+\)[^\n]*\]\(#[\w-]+\))
