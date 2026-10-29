---
type: regex
target: trace
flags: "i"
---
"command":"(?:[^"\\]|\\.)*?(?:\b|\\n)git\s+commit\b(?:[^"\\]|\\.)*(cursor|pagination|off-by-one|\bnext\b)
