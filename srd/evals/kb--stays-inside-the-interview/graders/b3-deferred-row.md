---
type: regex
target: {source: file, path: kb/_open-questions.md}
flags: "im"
---
^\|[^\n]*(empty|blank|optional|required|null)[^\n]*\|\s*`?deferred`?\s*\|
