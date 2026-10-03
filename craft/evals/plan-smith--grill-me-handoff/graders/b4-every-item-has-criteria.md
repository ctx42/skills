---
type: regex
target: {source: file, path: tmp/csv-export-plan.md}
match: "not_contains"
flags: "im"
---
^## \d+\.(?:(?!^## |done when|acceptance|verified by)[\s\S])*(?=^## |(?![\s\S]))
