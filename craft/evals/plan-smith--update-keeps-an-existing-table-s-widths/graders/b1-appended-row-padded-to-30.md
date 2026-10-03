---
type: regex
target: {source: file, path: tmp/wide-column-plan.md}
flags: "m"
---
^\| 4  \|(?= [^ |])[^|\n]{30}(?<= )\| N      \|$
