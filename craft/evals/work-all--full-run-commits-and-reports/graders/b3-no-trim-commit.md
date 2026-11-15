---
type: regex
target:
  source: file
  path: text/.git/logs/HEAD
flags: "i"
match: not_contains
---
\tcommit: [^\n]*\btrim\b
