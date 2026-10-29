---
type: regex
target: {source: file, path: README.md}
flags: "m"
---
^# [^\n]*\n[\s\S]*?!\[[^\]\n]*\]\((\./)?assets/logo\.png\)[\s\S]*?^## 
