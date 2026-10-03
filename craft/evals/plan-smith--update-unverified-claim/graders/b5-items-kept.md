---
type: regex
target: {source: file, path: rate-limit-plan.md}
flags: "m"
---
^(?=[\s\S]*^\| 1 +\| Token bucket +\| Y +\|$)(?=[\s\S]*^## 1\. Token bucket — \[x\]$)(?=[\s\S]*^## 2\. Redis counters)(?=[\s\S]*^## 3\. 429 responses)
