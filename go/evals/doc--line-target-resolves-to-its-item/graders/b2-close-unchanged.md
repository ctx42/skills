---
type: regex
target: {source: file, path: pkg/svc/foo.go}
---
\/\/ Close marks the svc closed\.\nfunc \(svc \*Svc\) Close\(\) \{\n\t\/\/ set closed to true\n\tsvc\.closed = true\n\}\n
