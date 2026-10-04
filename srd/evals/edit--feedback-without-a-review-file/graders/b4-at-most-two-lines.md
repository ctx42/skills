---
type: regex
target: last_message
match: not_contains
flags: "m"
---
(?:^(?!.*(?:policy|directive|approval))[^\n]*\S[^\n]*$[\s\S]*?){3}
