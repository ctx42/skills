---
type: regex
target: last_message
flags: "i"
---
notes[^\n]{0,200}(?:no[- ]repo|not a (?:git )?repo|outside|without (?:a )?(?:git )?repo|no commit|uncommitted)|(?:no[- ]repo|outside any|without (?:a )?(?:git )?repo)[^\n]{0,200}notes
