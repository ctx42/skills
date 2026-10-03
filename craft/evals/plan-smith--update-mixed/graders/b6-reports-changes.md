---
type: regex
target: last_message
flags: "i"
---
^(?=[\s\S]*login)(?=[\s\S]*session)(?=[\s\S]*(docs|operator))(?=[\s\S]*(force[- ]?logout|log ?out))
