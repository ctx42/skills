---
type: regex
target: last_message
flags: "is"
---
^(?=.*invalidat)(?=.*\b(stor(e|age)|where|redis|memcached|in-memory|cdn)\b)(?=.*\bkeys?\b)(?=.*\b(what|which)\b[^\n]{0,40}(cach|endpoint|data|response))
