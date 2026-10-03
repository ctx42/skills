---
type: regex
target: {source: file, path: go/skills/style/SKILL.md}
flags: "i"
---
\n## Test\n[\s\S]*\n- (?=[^\n]*naked return)[^\n]{1,100}\n
