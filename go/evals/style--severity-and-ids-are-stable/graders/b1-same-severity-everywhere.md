---
type: regex
target: last_message
match: not_contains
flags: "m"
---
(every-exported-symbol|receivers-three-letter-type)[\s\S]*^\W*(Blocker|Should-fix|Nit)s?\W*$[\s\S]*\1
