---
type: regex
target: {source: file, path: pkg/svc/foo_test.go}
match: not_contains
---
func Test_Encode(\(|_(?!tabular\()\w*\()
