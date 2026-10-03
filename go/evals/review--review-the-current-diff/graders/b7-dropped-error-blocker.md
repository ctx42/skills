---
type: regex
target: last_message
flags: "m"
---
Blocker(?:(?!Should-fix|\bNits?\b)[\s\S])*?store\.go:27\b(?=(?:(?!^\s*\d+\.|^#)[\s\S])*?(Load\(|missing|nonexistent|unreadable|permission))
