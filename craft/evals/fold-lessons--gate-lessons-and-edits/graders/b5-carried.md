---
type: regex
target: last_message
flags: "i"
---
[^\n]*(?:co-authored-by[^\n]*\b(?:reword|merge|already carried)|\b(?:reword|merge|already carried)[^\n]*co-authored-by)
