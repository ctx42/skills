---
type: regex
target: trace
match: not_contains
---
"name":"(?:Agent|Task|Write|Bash)","input":\{(?:"[^"]*":(?:"(?:[^"\\]|\\.)*"|[^,}"]*),)*"[^"]*":"(?:[^"\\]|\\.)*?(?<!no-)\bwork-init
