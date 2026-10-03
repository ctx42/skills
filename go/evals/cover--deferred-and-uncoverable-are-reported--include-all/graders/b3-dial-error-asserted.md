---
type: regex
target: {source: file, path: pkg/net/dial_test.go}
---
dialer\s*=|\w*[Dd]ialer\(t\b|[Ff]ake\w*[Dd]ialer\b
