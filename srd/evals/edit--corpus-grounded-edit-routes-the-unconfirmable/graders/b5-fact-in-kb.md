---
type: regex
target: {source: file, path: kb/_inbox.md}
flags: "i"
---
(three|\b3\b)[\s\S]{0,80}retr|retr[\s\S]{0,80}(three|\b3\b)
