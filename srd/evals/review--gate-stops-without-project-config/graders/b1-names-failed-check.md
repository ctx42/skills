---
type: regex
target: last_message
flags: "i"
---
^(?=[\s\S]*project-config\.md)(?=[\s\S]*(not found|no `?project-config|missing|(could ?n.t|could not|cannot) find))(?=[\s\S]*parent)
