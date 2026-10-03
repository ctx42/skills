---
type: regex
target: last_message
flags: "i"
match: not_contains
---
\b(400|800)\s?ms\b|\b0?\.[48]\s?s\b|\b1\.6\s?s\b
