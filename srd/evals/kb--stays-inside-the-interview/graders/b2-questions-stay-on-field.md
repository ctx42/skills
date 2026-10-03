---
type: regex
target: trace
match: not_contains
flags: "i"
---
\{"type":"assistant"[^\n]*"type":"text","text":"(?![^\n]*(sensor|field|empty|blank|tag|value|vib|hyd))[^\n]*\?
