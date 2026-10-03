---
type: regex
target: last_message
flags: "i"
---
(go test|gate|race)[^\n]*(pass|green|\bok\b)|(pass|green|\bok\b)[^\n]*(go test|gate|race)
