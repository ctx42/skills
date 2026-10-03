---
type: regex
target: trace
match: not_contains
flags: "i"
---
\{"type":"assistant"[^\n]*"type":"text","text":"[^\n]*(figma|design[- ]tool|(design|mock-?up)s? (link|url)|link to (the |a |an )?(approved )?design)[^\n]*\?
