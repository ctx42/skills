---
type: regex
target: {source: file, path: pkg/svc/foo.go}
---
\/\/ New returns an empty Svc\.\nfunc New\(\) \*Svc \{\n\treturn &Svc\{\}\n\}\n
