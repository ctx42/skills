---
type: regex
target: {source: file, path: kb/_inbox.md}
flags: "m"
---
^## [^\n]+\n+> (Not in the platform docs|Contradicts)[^#]*X-Api-Key
