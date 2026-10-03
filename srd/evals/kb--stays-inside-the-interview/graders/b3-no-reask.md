---
type: regex
target: trace
match: not_contains
flags: "i"
---
skip that for now[\s\S]*\{"type":"assistant"[^\n]*"type":"text","text":"[^\n]*(empty|blank)[^\n]*\?
