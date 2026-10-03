---
type: regex
target: {source: file, path: tmp/done-plan.md}
flags: "m"
---
^(?=[\s\S]*^## 1\. Filtered scope — \[x\]$)(?=[\s\S]*^## 2\. Row limit — \[x\]$)(?=[\s\S]*^## 4\. Remove this plan)
