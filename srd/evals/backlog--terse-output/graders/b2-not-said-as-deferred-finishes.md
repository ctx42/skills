---
type: regex
target: trace
match: not_contains
flags: "i"
---
\{"type":"assistant"[^\n]*"type":"text","text":"[^\n]*\b(both|2|two) (deferred )?(questions? )?(are )?(closed|answered|done)[\s\S]*"name":"mcp__srd-doc__resolve_gap"
