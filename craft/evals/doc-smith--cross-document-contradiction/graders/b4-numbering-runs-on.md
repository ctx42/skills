---
type: regex
target: last_message
match: "not_contains"
flags: "i"
---
Should[- ]?fix[^\n]*\n(?:\s*\n)*\s*(?:[-*]\s+)?(?:\*\*)?1[.)]
