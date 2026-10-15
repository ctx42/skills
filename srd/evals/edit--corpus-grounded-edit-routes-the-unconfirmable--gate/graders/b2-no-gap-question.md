---
type: regex
target: last_message
match: not_contains
flags: "i"
---
(gap|backlog|documentation)[^.?!]{0,200}\?
