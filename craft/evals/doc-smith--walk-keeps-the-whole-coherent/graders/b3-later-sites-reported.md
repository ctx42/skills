---
type: regex
target: last_message
flags: "i"
---
^(?=[\s\S]*\bworkspaces?\b)(?=[\s\S]*(\blines?\s*\d+|\bL\d+|\.md:\d+|Creating a workspace|Inviting your team|Archiving a workspace))
