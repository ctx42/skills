---
type: regex
target: last_message
flags: "i"
---
draft[^.\n]{0,60}\b(none|no|nothing|0)\b|\b(no|none|zero)\b[^.\n]{0,40}draft
