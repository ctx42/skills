---
type: regex
target: {source: file, path: tmp/wide-column-plan.md}
flags: "im"
---
^(?=[\s\S]*^## 4\. [^\n]*quota[^\n]* — \[ \]$)(?=[\s\S]*^\| 4  \|[^|\n]*quota[^|\n]*\| N      \|$)
