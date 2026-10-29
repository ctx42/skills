---
type: regex
target: {source: file, path: initiatives/password-reset/srd.md}
match: not_contains
flags: "im"
---
^- `[A-Z]+-\d+[a-z]?`(?:(?!\n\s*\n|\n- )[\s\S])*?\bsecure(ly)?\b
