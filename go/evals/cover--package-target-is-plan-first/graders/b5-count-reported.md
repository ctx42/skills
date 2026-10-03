---
type: regex
target: last_message
flags: "i"
---
\b\d+\s+(new\s+)?(cases?|rows?|subtests?)\b|cases?\s+added[^\d\n]{0,25}\d+
