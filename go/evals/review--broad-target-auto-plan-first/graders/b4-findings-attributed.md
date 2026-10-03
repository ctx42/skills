---
type: regex
target: last_message
flags: "m"
---
^\s*(?:\d+\.|[-*])\s+`?(?:api|auth|cache|config|events|httpx|logx|metrics|queue|retry|worker)/|^#{2,4}[^\n]*\b(?:api|auth|cache|config|events|httpx|logx|metrics|queue|retry|worker)\b|^\|\s*`?(?:api|auth|cache|config|events|httpx|logx|metrics|queue|retry|worker)`?\s*\|
