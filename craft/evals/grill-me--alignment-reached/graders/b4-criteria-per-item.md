---
type: regex
target: {source: file, path: plans/csv-export.md}
flags: "i"
---
(done when|acceptance|pass(es)? when|verified when)([\s\S]*?(done when|acceptance|pass(es)? when|verified when)){6}
