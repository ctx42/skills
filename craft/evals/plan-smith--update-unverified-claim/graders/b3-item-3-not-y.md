---
type: regex
target: {source: file, path: rate-limit-plan.md}
flags: "m"
---
^(?=[\s\S]*^\| 3 +\| 429 responses +\| N +\|$)(?=[\s\S]*^## 3\. 429 responses — \[ \]$)
