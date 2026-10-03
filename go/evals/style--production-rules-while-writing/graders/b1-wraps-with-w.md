---
type: regex
target: {source: file, path: service.go}
---
fmt\.Errorf\("[a-z][^"%]*: %w"|errors\.Join\(
