---
type: regex
target: last_message
match: not_contains
flags: "i"
---
(\bbank\b|(add|record|save|write|capture|keep) (this|it|that|these)[^.?!]{0,60}(knowledge base|\bkb\b|inbox))[^.?!]*\?
