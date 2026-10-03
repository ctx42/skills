---
type: regex
target: trace
match: not_contains
---
"name":"(?:Agent|Task|Write)","input":\{(?:"[^"]*":(?:"(?:[^"\\]|\\.)*"|[^,}"]*),)*"[^"]*":"(?:[^"\\]|\\.)*?match-errors-(is|as|errorsis|errorsas)\b
