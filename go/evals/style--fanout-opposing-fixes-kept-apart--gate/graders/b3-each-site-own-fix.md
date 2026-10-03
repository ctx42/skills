---
type: regex
target: last_message
match: not_contains
flags: "i"
---
\b(delete|remove)\b(?:(?!\b(?:insert|add|delete|remove)\b)[\s\S])*?\b(alpha|bravo|charlie|delta)_test\.go|\b(insert|add)\b(?:(?!\b(?:insert|add|delete|remove)\b)[\s\S])*?\b(echo|foxtrot|golf|hotel)_test\.go
