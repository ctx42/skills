---
type: regex
target: {source: file, path: metrics/metrics.go}
---
\/\/ Package metrics counts events\.\npackage metrics\n\n\/\/ Counter counts events\.\ntype Counter struct \{\n\tn int\n\}\n\nfunc \(cnt \*Counter\) Inc\(\) \{\n\t\/\/ add one\n\tcnt\.n\+\+\n\}\n
