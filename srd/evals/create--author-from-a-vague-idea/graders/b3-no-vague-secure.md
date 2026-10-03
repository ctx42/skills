---
type: regex
target: {source: file, path: initiatives/password-reset/srd.md}
match: not_contains
flags: "i"
---
\*\*[A-Z]+-\d+[a-z]?:\*\*[^*]*\bsecure(ly)?\b
