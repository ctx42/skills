---
type: regex
target: {source: file, path: tmp/done-plan.md}
flags: "m"
---
^(?=[\s\S]*^## 4\. Remove this plan — \[ \]$)(?=[\s\S]*^\| 4  \| Remove this plan  \| N      \|$)
