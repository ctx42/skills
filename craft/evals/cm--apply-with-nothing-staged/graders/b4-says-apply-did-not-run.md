---
type: regex
target: last_message
flags: "i"
---
(apply|commit)[^\n]{0,80}(\bnot|n't|\bskipped)\b|(\bnot|n't|\bno)\b[^\n]{0,60}\b(commit|apply)
