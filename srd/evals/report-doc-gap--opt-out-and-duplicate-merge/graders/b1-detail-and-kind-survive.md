---
type: regex
target: mock_calls
flags: "m"
match: not_contains
---
^(?=[^\n]*"tool":"[^"]*update_gap")(?![^\n]*never states how many times)|^(?=[^\n]*"tool":"[^"]*update_gap")(?![^\n]*"kind":"missing")
