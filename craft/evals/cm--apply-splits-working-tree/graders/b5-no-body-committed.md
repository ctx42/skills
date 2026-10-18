---
type: regex
target: trace
match: not_contains
---
"command":"(?:[^"\\]|\\.)*?(?:\b|\\n)git\s+commit\b(?:(?!\\n)[^"\\<]|\\[^n])*<<\s*'?(\w+)'?\\n[^\\\"]+\\n(?!\1\b|\\n(?:BREAKING CHANGE|Refs): )
