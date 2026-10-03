---
type: regex
target: trace
match: not_contains
---
"command":"(?:[^"\\]|\\.)*?\bgit\s+commit\b(?:[^"\\]|\\.)*<<\s*'?(\w+)'?\\n[^\\\"]+\\n(?!\1\b)
