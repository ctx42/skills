---
type: regex
target: last_message
match: not_contains
flags: "m"
---
[Vv]erdict[\s\S]*(foo(_test)?\.go:\d+|`[a-z0-9]+(-[a-z0-9]+){2,}`)|^\W*(Summary|Recap)\b
