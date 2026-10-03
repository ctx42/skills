---
type: regex
target: last_message
match: not_contains
flags: "mi"
---
^\s*\d+\.[^\n]*(foo\.go:2[12]\b|<= k|off-by-one)
