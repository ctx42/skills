---
type: regex
target: {source: file, path: go/skills/style/SKILL.md}
match: "not_contains"
flags: "i"
---
\n## Test\n[\s\S]*\n- [^\n]*naked return[^\n]*\n(  [^\n]+\n){2,}
