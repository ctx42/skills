---
type: regex
target: last_message
match: "count:1"
flags: "i"
---
(\b5\b|\bfive\b)[^\n\d]{0,30}gap|gap[^\n\d]{0,30}(\b5\b|\bfive\b)
