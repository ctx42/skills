---
type: regex
target: {source: file, path: README.md}
match: "not_contains"
flags: "i"
---
10[,.]?000|\b10k\b|ports?/s|per second|benchmark|blazing|lightning
