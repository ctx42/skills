---
type: regex
target: {source: file, path: README.md}
match: "not_contains"
flags: "i"
---
\bgo\s*(>=?\s*)?1\.\d+|\bgo1\.\d+
