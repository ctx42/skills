---
type: regex
target: last_message
flags: "i"
---
[^\n]*(?:acme[^\n]*\brevert|\brevert[^\n]*acme)
