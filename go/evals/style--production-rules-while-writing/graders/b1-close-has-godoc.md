---
type: regex
target: {source: file, path: service.go}
---
// Close [^\n]*\n(//[^\n]*\n)*func \(\w+ \*Service\) Close\(\)
