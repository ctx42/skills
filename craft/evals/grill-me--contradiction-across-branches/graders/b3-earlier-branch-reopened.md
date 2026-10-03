---
type: regex
target: last_message
flags: "i"
---
reopen\w*[\s\S]{0,80}?(data[- ]model|offline|branch 1)|(data[- ]model|offline[- ]first|branch 1)[^\n]{0,60}(reopen\w*|open again|back (to )?open|unresolved|not resolved|no longer resolved)
