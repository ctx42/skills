---
type: regex
target: {source: file, path: api/api.go}
match: "not_contains"
flags: "i"
---
concurren|goroutine|synchroni|thread|safe for|mutex|lock
