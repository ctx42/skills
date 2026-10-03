---
type: regex
target: trace
match: not_contains
flags: "i"
---
\{"type":"assistant"[^\n]*"type":"text","text":"[^\n]*(list_gaps|let me (list|fetch|pull|load|get|check) (the )?(open )?gaps|listing (the )?(open )?gaps)
