---
type: regex
target: last_message
flags: "i"
---
fileSink[^\n]*(remov|delet|drop|strip)
