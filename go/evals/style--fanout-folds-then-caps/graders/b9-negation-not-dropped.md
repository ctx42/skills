---
type: regex
target: trace
match: not_contains
---
"name":"(?:Agent|Task|Write)","input":\{(?:"[^"]*":(?:"(?:[^"\\]|\\.)*"|[^,}"]*),)*"[^"]*":"(?:[^"\\]|\\.)*?(?<!no-)\bwork-init
