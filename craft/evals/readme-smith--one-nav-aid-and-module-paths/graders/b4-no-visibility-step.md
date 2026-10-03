---
type: regex
target: {source: file, path: README.md}
match: "not_contains"
flags: "i"
---
GOPRIVATE|GONOSUMDB|GONOPROXY|private (repo|repository|module)|public (repo|repository|module)
