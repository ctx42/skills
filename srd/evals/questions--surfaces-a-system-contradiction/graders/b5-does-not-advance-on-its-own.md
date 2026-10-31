---
type: regex
target: last_message
match: not_contains
flags: "m"
---
(?:300 ms|5 working days)[\s\S]*^(?![ \t]*>)[^\n]*\*\*Q\d+:?\*\*[^\n]*\?
