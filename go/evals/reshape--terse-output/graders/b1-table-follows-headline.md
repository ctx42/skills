---
type: regex
target: last_message
flags: "i"
---
\b\d+\s+uses\b[^\n]*\n(?:[^|\n][^\n]*\n|\s*\n){0,4}\s*\|\s*#\s*\|
