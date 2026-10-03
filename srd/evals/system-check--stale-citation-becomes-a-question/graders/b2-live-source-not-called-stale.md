---
type: regex
target: trace
match: not_contains
flags: "i"
---
\{"type":"assistant"[^\n]*"type":"text","text":"[^"\n]*sound_file_documentation(\.md)?[^.\n"]{0,100}(stale|gone|no longer|missing|vanished)
