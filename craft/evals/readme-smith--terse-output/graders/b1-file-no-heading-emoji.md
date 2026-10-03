---
type: regex
target: {source: file, path: README.md}
match: "not_contains"
flags: "mu"
---
^#+ [^\n]*[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]
