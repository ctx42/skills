---
type: regex
target: {source: file, path: go/skills/style/SKILL.md}
match: "not_contains"
flags: "i"
---
compile[- ]time|\(\*T\)\(nil\)
