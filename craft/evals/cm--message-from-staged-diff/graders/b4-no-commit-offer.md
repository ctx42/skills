---
type: regex
target: last_message
flags: "i"
match: not_contains
---
(want me to|shall I|should I|I can)[^\n]{0,40}commit|commit (it|this)\?
