---
type: regex
target: {source: file, path: initiatives/password-reset/srd.md}
flags: "im"
---
^- `[A-Z]+-\d+[a-z]?`(?:(?!\n\s*\n|\n- )[\s\S])*?\b30\s*minutes
