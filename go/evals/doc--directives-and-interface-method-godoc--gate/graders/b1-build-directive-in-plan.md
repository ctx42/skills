---
type: regex
target: last_message
flags: "i"
---
go:build[^\n]*(never|directive|untouch|leave|skip)|(never|directive|untouch)[^\n]*go:build
