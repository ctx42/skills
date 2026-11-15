---
type: regex
target: last_message
flags: "i"
---
mirror[^\n]{0,200}(?:skip|read-only|forbid)|(?:skip|read-only|forbid)[^\n]{0,200}mirror
