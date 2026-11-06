---
type: regex
target: last_message
flags: "is"
---
^(?=.*(?:summary|shared understanding|acceptance|pass if|pass/fail|criteri))(?!.*\?[*_\s]*(?:\n[^\n]*(?:policy|directive|approval)[^\n]*\s*)*$)
