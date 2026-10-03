---
type: regex
target: {source: file, path: README.md}
match: "not_contains"
flags: "i"
---
TODO[^\n]*(benchmark|throughput|ports?/s|performance|speed|fast)
