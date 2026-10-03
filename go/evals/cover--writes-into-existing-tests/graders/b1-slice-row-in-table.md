---
type: regex
target: {source: file, path: pkg/svc/foo_test.go}
---
func Test_Encode_tabular[\s\S]*\[\]int\{[^}]*\},\s*"\[[^"]*",?\s*\}
