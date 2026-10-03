---
type: regex
target: {source: file, path: pkg/sink/sink.go}
flags: "i"
---
//[^\n]*(ignor|discard|swallow|hid|drop|unreported|not report|len\(p\)|even (if|when))[^\n]*\n(//[^\n]*\n)*func \(tee \*teeSink\) Write\(
