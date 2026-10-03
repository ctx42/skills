---
type: regex
target: last_message
match: not_contains
flags: "mi"
---
^\s*(?:[-*]\s+)?\**fix(?:es)?\**:\**\s*\**`?(?!(?:insert|delete|rename|move|replace|reword)\b)[a-z]|^\s*(?:\d+\.|-)\s*\*\*(?:add|remove|change|put|drop)\b
