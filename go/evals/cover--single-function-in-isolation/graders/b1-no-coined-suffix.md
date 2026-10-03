---
type: regex
target: {source: file, path: pkg/cfg/parse_test.go}
match: not_contains
---
func Test_Parse_(?!tabular\()
