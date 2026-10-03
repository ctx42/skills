---
type: regex
target: {source: file, path: README.md}
match: "not_contains"
---
<!-- gmmce:[^\n]*-->\n```go\n(?:(?!```)[^\n]*\n)*?[ \t]*(package |func |import )
