---
type: regex
target: {source: file, path: rate-limit-plan.md}
flags: "m"
---
^(?=[\s\S]*^\| 2 +\| Redis counters +\| N +\|$)(?=[\s\S]*^## 2\. Redis counters — \[ \]$)
