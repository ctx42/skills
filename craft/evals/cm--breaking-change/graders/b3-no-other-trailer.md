---
type: regex
target: last_message
flags: "m"
match: not_contains
---
^(?!BREAKING CHANGE:|Refs:)(?:[A-Z][A-Za-z]*-[A-Za-z-]+|Closes|Fixes|Resolves|Ticket):\s
