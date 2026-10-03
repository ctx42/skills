---
type: regex
target: files
match: not_contains
flags: "m"
---
(^|/)kb/(?!_inbox\.md$|_open-questions\.md$)\S+$
