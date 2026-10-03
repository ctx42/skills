---
type: regex
target: last_message
flags: "i"
---
^\s*(?:#[^\n]*\n+\s*)?(?:[^\n]*(?:grep|language server|LSP)[^\n]*\n+\s*)?[^\n|]*\bmust\b[^\n|]*\b\d+\s+uses\b
