---
type: regex
target: last_message
flags: "i"
match: not_contains
---
\b(ask me to|want me to|shall I|should I|I can|I could|to)\s+(\w+\s+){0,2}amend|/cm\b[^\n]*\bapply\b|--amend
