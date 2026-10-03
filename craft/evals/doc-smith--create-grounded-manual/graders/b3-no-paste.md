---
type: regex
target: last_message
match: "not_contains"
flags: "m"
---
^#{1,3} [^\n]+\n(?:[\s\S]*?^#{1,3} [^\n]+\n){3}
