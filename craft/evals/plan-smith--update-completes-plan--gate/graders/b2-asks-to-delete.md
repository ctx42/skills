---
type: regex
target: last_message
flags: "i"
---
(delete|remove)[^\n]{0,80}(plan|file)|(plan|file)[^\n]{0,80}(delete|remov)
