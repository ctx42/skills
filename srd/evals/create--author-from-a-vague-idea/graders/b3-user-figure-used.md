---
type: regex
target: {source: file, path: initiatives/slot-swap/srd.md}
flags: "im"
---
^- `[A-Z]+-\d+[a-z]?`(?:(?!\n\s*\n|\n- )[\s\S])*?\b14\s*days
