---
type: regex
target: last_message
flags: "m"
---
^```[a-z]*\n(?=[^\n]{1,56}\n)feat(\([a-z0-9/_.-]+\))?: (?![a-z]+(?:ed|ing|s)\b)[a-z][^\n]*[^.\n]\n
