---
type: regex
target: last_message
match: not_contains
flags: "mi"
---
^\s*\d+\.(?:(?!^\s*\d+\.)[\s\S])*?(?:insert[^\n]*blank line(?:(?!^\s*\d+\.)[\s\S])*?delete[^\n]*blank line|delete[^\n]*blank line(?:(?!^\s*\d+\.)[\s\S])*?insert[^\n]*blank line)
