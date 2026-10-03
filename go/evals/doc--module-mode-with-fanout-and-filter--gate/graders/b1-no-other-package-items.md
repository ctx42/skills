---
type: regex
target: last_message
match: "not_contains"
---
\b(auth|cache|config|events|httpx|logx|metrics|queue|retry)(/\w+)?\.go\b
