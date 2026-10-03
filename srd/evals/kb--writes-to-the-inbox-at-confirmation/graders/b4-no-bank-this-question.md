---
type: regex
target: trace
match: not_contains
flags: "i"
---
\{"type":"assistant"[^\n]*"type":"text","text":"[^\n]*(\bbank\b|(add|record|save|write|capture|keep) (this|it|that|these)[^.?!\\]{0,60}(knowledge base|\bkb\b|inbox))[^.?!\\]*\?
