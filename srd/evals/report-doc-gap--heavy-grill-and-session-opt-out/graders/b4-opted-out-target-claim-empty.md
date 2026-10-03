---
type: regex
target: mock_calls
flags: "m"
match: not_contains
---
^(?=[^\n]*"tool":"[^"]*update_gap")(?=[^\n]*"gap_id":"gap-031[23]")(?=[^\n]*"target_claim":"[^"\\])
