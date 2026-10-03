---
type: regex
target: {source: file, path: pkg/io/io.go}
---
\/\/go:build !windows\n\n\/\/ Package io serves bytes from an in-memory buffer\.\npackage io\n\nimport "io"\n\n\/\/go:generate stringer -type=Mode\n\n\/\/ Mode selects how a Source treats its buffer\.\ntype Mode int\n\n\/\/ Source modes\.\nconst \(\n\tModeCopy Mode = iota\n\tModeShare\n\)\n\nvar _ io\.Reader = \(\*Source\)\(nil\)\n\n\/\/ Source reads from a fixed byte slice\.\ntype Source struct \{\n\tbuf \[\]byte\n\toff int\n\}\n\n\/\/ NewSource returns a Source that reads buf\.\nfunc NewSource\(buf \[\]byte\) \*Source \{\n\treturn &Source\{buf: buf\}\n\}\n\n\/\/ Read reads up to len\(p\) bytes into p\. It returns the number of bytes\n\/\/ read and any error encountered\. At end of input it returns 0, io\.EOF\.\nfunc \(src \*Source\) Read\(p \[\]byte\) \(int, error\) \{\n\tif src\.off >= len\(src\.buf\) \{\n\t\treturn 0, io\.EOF\n\t\}\n\tn := copy\(p, src\.buf\[src\.off:\]\)\n\tsrc\.off \+= n\n\treturn n, nil\n\}\n
