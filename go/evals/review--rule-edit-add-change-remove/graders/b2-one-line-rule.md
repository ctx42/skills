---
type: regex
target: {source: file, path: go/skills/style/references/test.md}
match: "not_contains"
flags: "i"
---
\n- [^\n]*naked return[^\n]*\n(  [^\n]+\n){2,}
