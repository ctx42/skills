---
type: regex
target: trace
match: not_contains
flags: "i"
---
^(?:(?!"name":"mcp__srd__glossary_terms")[\s\S])*\{"type":"assistant"[^\n]*"type":"text","text":"[^\n]*\b(in|out of) scope\b[^\n]*\?
