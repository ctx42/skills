---
type: regex
target: last_message
flags: "i"
---
^(?=[\s\S]*(\d+\s*(open\s+)?blockers?|blockers?\W{0,3}\d+))(?=[\s\S]*(\d+\s*major|major\W{0,3}\d+))
