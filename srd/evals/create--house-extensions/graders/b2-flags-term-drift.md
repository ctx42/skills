---
type: regex
target: last_message
flags: "i"
---
evidence[^\n]{0,120}measurement|measurement[^\n]{0,120}evidence
