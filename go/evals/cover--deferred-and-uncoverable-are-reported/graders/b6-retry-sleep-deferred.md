---
type: regex
target: last_message
flags: "i"
---
(deferred|complex)[\s\S]*retry\.go:[0-9,–\- ]*\b1[34]\b[^\n]*(sleep|wait|100\s?ms|slow)
