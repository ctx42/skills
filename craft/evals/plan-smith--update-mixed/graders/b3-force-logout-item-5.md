---
type: regex
target: {source: file, path: sso-plan.md}
flags: "im"
---
^(?=[\s\S]*^## 5\. [^\n]*(log ?out|sign[- ]?out)[^\n]* — \[ \]$)(?=[\s\S]*^\| 5 +\|[^|\n]*(log ?out|sign[- ]?out)[^|\n]*\| N +\|$)
