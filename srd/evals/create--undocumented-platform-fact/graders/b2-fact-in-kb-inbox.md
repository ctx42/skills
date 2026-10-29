---
type: regex
target: {source: file, path: kb/_inbox.md}
flags: "i"
---
retr[\s\S]*\b(three|3)\b|\b(three|3)\b[\s\S]*retr
