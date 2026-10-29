---
type: regex
target: last_message
flags: "is"
---
^(?=.*\bhold)(?=.*\b(draft|gap-\d{4})\b)(?=.*(\?|\bfile\b))
