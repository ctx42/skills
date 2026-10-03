---
type: regex
target: {source: file, path: auth/auth.go}
---
\/\/ Package auth checks bearer tokens\.\npackage auth\n\nimport "strings"\n\nfunc Token\(header string\) string \{\n\treturn strings\.TrimPrefix\(header, "Bearer "\)\n\}\n
