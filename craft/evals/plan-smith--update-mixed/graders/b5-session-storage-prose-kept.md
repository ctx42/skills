---
type: regex
target: {source: file, path: sso-plan.md}
flags: "m"
---
^## 3\.[^\n]*\n\nSessions live in Redis, keyed by an opaque session ID, with a 12-hour TTL\. The\ncookie carries only the ID\.\n\nDone when: a session survives an app restart, expires on its own after 12\nhours, and logout deletes the key\.\n
