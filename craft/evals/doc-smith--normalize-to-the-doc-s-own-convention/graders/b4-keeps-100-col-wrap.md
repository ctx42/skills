---
type: regex
target: {source: file, path: docs/guide.md}
flags: "m"
---
(?:^[^|#\n][^\n]{85,99}$[\s\S]*?){3}
