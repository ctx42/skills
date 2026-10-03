---
type: regex
target: {source: file, path: store/store.go}
---
^(?=[\s\S]*data, _ := os\.ReadFile)(?=[\s\S]*\"save %s: %v\")
