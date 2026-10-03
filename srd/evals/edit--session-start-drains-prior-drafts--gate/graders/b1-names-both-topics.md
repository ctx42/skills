---
type: regex
target: last_message
flags: "is"
---
^(?=.*retr)(?=.*(lockout duration|stays locked|locked by default|lock(out)? (period|time)|how long[^\n]{0,60}lock))
