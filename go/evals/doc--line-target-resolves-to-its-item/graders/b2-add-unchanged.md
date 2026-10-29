---
type: regex
target: {source: file, path: pkg/svc/foo.go}
---
\n\nfunc \(svc \*Svc\) Add\(line string\) error \{\n\tif svc\.closed \{\n\t\treturn ErrClosed\n\t\}\n\t\/\/ append the line\n\tsvc\.lines = append\(svc\.lines, strings\.TrimSpace\(line\)\)\n\treturn nil\n\}\n
