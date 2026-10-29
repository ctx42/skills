---
type: regex
target: last_message
flags: "m"
---
Blocker(?:(?!Should-fix|\bNits?\b)[\s\S])*?store\.go:34\b(?=(?:(?!^\s*\d+\.|^#)[\s\S])*?correctness)(?=(?:(?!^\s*\d+\.|^#)[\s\S])*?(wrap-errors-w|%w))
