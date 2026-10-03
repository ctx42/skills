---
type: regex
target: last_message
match: not_contains
flags: "m"
---
(?:^(?!.*(?:Weisung|AI-Agents|freigabe|directive))[^\n]*\S[^\n]*$[\s\S]*?){3}
