---
type: regex
target:
  source: file
  path: fetch.go
---
defer resp\.Body\.Close\(\)[\s\S]*StatusCode != http\.StatusOK
