---
type: regex
target: trace
match: not_contains
flags: "i"
---
\{"type":"assistant"[^\n]*"type":"text","text":"[^\n]*(doc(umentation)? gap|report (it|this|that|a gap)|file (it|this|that|a gap)|\bbank\b|knowledge base|\bkb\b|inbox)[^\n]*\?[\s\S]*"name":"Write","input":\{"file_path":"[^"]*initiatives/
