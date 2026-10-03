---
type: regex
target: last_message
flags: "i"
match: not_contains
---
(want me to|shall I|should I|I can|let me know)[^\n]{0,60}|commit (it|this)\?
