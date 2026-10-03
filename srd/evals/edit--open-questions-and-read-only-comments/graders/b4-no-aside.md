---
type: regex
target: trace
match: not_contains
---
(Skip|\*\*S\*\*kip)\s*/\s*(Edit|\*\*E\*\*dit)\)?(?:\\n|\s){1,6}[^"#*>\-U][^"]{0,300}\?
