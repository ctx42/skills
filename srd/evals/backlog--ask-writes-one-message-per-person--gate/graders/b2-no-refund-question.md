---
type: regex
target: last_message
match: not_contains
flags: "i"
---
^(?:[^`]|`(?!``))*(?:```[a-z]*\n(?:(?!```)[\s\S])*```(?:[^`]|`(?!``))*)*?```[a-z]*\n(?:(?!```)[\s\S])*?refund
