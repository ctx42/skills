---
type: regex
target: {source: file, path: tmp/agent-plan-csv-export.md}
match: "not_contains"
flags: "im"
---
^## \d+\.(?:(?!^## |done when|acceptance|verified by)[\s\S])*(?=^## |(?![\s\S]))
