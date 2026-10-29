---
type: regex
target: last_message
match: "count:1"
flags: "i"
---
(\b3\b|\bthree\b)[^\n\d]{0,30}deferred|deferred[^\n\d]{0,30}(\b3\b|\bthree\b)
