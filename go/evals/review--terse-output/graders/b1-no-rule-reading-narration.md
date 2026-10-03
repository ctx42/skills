---
type: regex
target: last_message
match: "not_contains"
flags: "i"
---
(read|loaded|loading|reading|consulted)[^.\n]{0,30}(rules|rulebook|style guide|SKILL\.md|checking\.md)
