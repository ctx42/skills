---
type: regex
target: last_message
flags: "i"
---
stale[^\n]{0,80}(reopen|refresh)|(reopen|refresh)[^\n]{0,80}stale
