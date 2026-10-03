---
type: regex
target: last_message
flags: "i"
---
(gofmt[^\n]*go build|go build[^\n]*gofmt)[^\n]*\b(pass|passed|clean|ok|succeed)|\b(pass|passed|clean|ok|succeed)\w*\b[^\n]{0,20}(gofmt[^\n]*go build|go build[^\n]*gofmt)
