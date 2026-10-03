---
type: regex
target: last_message
flags: "i"
---
(apply|commit)[^\n]{0,80}\b(not|n't|skipped)\b|\b(not|n't|no)\b[^\n]{0,60}\b(commit|apply)
