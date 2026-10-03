---
type: regex
target: trace
match: not_contains
---
"name":"(?:Agent|Task|Write|Bash)","input":\{(?:"[^"]*":(?:"(?:[^"\\]|\\.)*"|[^,}"]*),)*"[^"]*":"(?:[^"\\]|\\.)*?match-errors-(is|as|errorsis|errorsas)\b
