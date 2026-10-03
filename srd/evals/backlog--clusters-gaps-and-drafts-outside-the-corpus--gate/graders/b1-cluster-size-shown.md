---
type: regex
target: last_message
flags: "i"
---
(\b2\b|\btwo\b)[^\n\d]{0,20}(gaps?|reports?|duplicates?|times)\b|(size|reports|gaps|count)\W{0,5}(\b2\b|\btwo\b)
