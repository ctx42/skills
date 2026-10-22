---
type: regex
target: last_message
flags: "i"
---
[^\n]*(?:(?:PR #?412|export\.go|lesson \(?b\)?)[^\n]*\bdrop|\bdrop[^\n]*(?:PR #?412|export\.go|lesson \(?b\)?))
