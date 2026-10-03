---
type: regex
target: last_message
flags: "i"
---
^(?=[\s\S]*\b(insert|add)\b)(?=[\s\S]*\b(delete|remove)\b)
