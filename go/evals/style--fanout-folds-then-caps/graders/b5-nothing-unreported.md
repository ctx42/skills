---
type: regex
target: last_message
flags: "i"
---
\b0\b[^\n]{0,30}unreported|unreported[^\n]{0,30}\b0\b|(none|nothing|no offen[cs]es?)[^\n]{0,30}(unreported|cut|dropped)
