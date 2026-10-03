---
type: regex
target: {source: file, path: sso-plan.md}
flags: "m"
---
^(?=[\s\S]*^## 1\. Provider config — \[ \]$)(?=[\s\S]*^## 2\. Login flow — \[x\]$)(?=[\s\S]*^## 3\. Session storage — \[[x ]\]$)
