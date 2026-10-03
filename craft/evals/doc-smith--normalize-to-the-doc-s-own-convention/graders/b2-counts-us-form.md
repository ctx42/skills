---
type: regex
target: last_message
flags: "i"
---
(\b\d+\b|×\s*\d+|\b(one|two|three)\b)[^\n]{0,80}\bcolors?\b|\bcolors?\b[^\n]{0,80}(\b\d+\b|×\s*\d+|\b(one|two|three)\b)
