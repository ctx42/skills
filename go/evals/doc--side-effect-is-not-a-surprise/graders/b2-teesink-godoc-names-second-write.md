---
type: regex
target: {source: file, path: pkg/sink/sink.go}
flags: "i"
---
//[^\n]*(mirror|second|copy|also)[^\n]*\n(//[^\n]*\n)*func \(tee \*teeSink\) Write\(
