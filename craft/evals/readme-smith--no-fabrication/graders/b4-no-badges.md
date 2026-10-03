---
type: regex
target: {source: file, path: README.md}
match: "not_contains"
flags: "m"
---
^\[!\[|img\.shields\.io|badge\.svg|pkg\.go\.dev/badge
