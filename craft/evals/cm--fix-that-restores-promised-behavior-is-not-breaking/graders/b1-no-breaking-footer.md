---
type: regex
target: last_message
match: not_contains
---
^(?:(?!```)[\s\S])*```[a-z]*\n(?:(?!```)[^\n]*\n)*?BREAKING CHANGE
