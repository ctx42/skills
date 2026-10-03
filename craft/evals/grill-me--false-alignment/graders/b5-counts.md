---
type: regex
target: last_message
flags: "is"
---
\b(5|five)\s*(of|/)\s*6\b|^(?=.*\b(5|five)\b[^\n]{0,20}resolved)(?=.*\b(1|one)\b[^\n]{0,20}(open|remain\w*|left|outstanding))
