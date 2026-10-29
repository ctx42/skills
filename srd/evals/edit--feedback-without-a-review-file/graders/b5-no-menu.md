---
type: regex
target: last_message
match: not_contains
flags: "i"
---
srd:review|\b(run|use|try)\s+`?/?(srd:)?review\b|paste|drop(ping)?\s+(the|`#)|without\s+(the\s+)?`?#|re-?run
