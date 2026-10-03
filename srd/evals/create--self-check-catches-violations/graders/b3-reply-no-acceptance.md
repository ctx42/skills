---
type: regex
target: last_message
match: not_contains
flags: "i"
---
status[^\n]{0,30}\bACCEPTED\b|\b(is|now) acceptable\b|ready (for|to be) accept|set (it |the status )?to `?ACCEPTED
