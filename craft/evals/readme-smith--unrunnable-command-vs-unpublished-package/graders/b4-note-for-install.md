---
type: regex
target: {source: file, path: README.md}
flags: "i"
---
> \[!NOTE\][ \t]*\n(?:>[^\n]*\n)*?>[^\n]*(publish|releas|\btag|public)
