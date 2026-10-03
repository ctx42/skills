---
type: regex
target: {source: file, path: archive/archive.go}
flags: "i"
---
//[^\n]*(sort|reorder|in place|modif|mutat|order)[^\n]*\n(//[^\n]*\n)*func \(arc \*Archive\) Store\(
