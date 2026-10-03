---
type: regex
target: trace
flags: "i"
---
\{"type":"assistant"[^\n]*"type":"text","text":"[^\n]*(\bline\b[^\n]*\bLoad\b|\bLoad\b[^\n]*\bline\b)
