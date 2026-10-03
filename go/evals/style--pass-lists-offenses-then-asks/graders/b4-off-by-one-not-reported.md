---
type: regex
target: last_message
match: not_contains
flags: "mi"
---
foo\.go:2[12]\b|^\s*\d+\.[^\n]*(<= k|off-by-one)
