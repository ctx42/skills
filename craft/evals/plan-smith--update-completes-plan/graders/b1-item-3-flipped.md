---
type: regex
target: {source: file, path: tmp/done-plan.md}
flags: "m"
---
^(?=[\s\S]*^## 3\. Audit log — \[x\]$)(?=[\s\S]*^\| 3  \| Audit log {9}\| Y      \|$)
