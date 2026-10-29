---
type: regex
target: last_message
flags: "i"
---
[^\n]*(?:paste[^\n]*(?:held|hold|\?|decid|recommend)|(?:held|hold|\?|decid|recommend)[^\n]*paste)
