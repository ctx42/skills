---
type: regex
target: mock_calls
flags: "m"
match: not_contains
---
^(?=[^\n]*"tool":"[^"]*update_gap")(?=[^\n]*"target_claim":"[^"\\])
