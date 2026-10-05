---
type: regex
target: last_message
match: not_contains
---
^(?:[^`]|`(?!``))*(?:```[a-z]*\n(?:(?!```)[\s\S])*```(?:[^`]|`(?!``))*)*?```[a-z]*\n(?:(?!```)[\s\S])*?gap-\d
