---
type: regex
target: {source: file, path: go/skills/style/references/test.md}
flags: "i"
---
\n- (?=[^\n]*naked return)[^\n]{1,100}\n
