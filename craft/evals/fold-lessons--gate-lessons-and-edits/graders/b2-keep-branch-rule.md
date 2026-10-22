---
type: regex
target: last_message
flags: "i"
---
[^\n]*(?:branch[^\n]*\b(?:keep|generali[sz]e)|\b(?:keep|generali[sz]e)[^\n]*branch)
