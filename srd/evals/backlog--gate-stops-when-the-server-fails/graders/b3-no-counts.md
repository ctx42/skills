---
type: regex
target: last_message
match: not_contains
flags: "i"
---
\b[0-9]+\s+(deferred|unknowns?)\b|(deferred|unknowns?)\W{1,3}[0-9]+\b
