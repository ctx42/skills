---
type: regex
target: {source: file, path: initiatives/slot-swap/srd.md}
match: not_contains
flags: "im"
---
^- `[A-Z]+-\d+[a-z]?`(?:(?!\n\s*\n|\n- )[\s\S])*?\btimely\b
