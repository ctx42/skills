---
type: regex
target: {source: file, path: pkg/svc/foo.go}
---
\/\/ len returns the buffered lines\nfunc \(svc \*Svc\) Len\(\) int \{\n\treturn len\(svc\.lines\)\n\}\n
