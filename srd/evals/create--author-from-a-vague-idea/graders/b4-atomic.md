---
type: regex
target: {source: file, path: initiatives/password-reset/srd.md}
match: not_contains
flags: "im"
---
^- `[A-Z]+-\d+[a-z]?`(?:(?!\n\s*\n|\n- )[\s\S])*?(e-?mail(?:(?!\n\s*\n|\n- )[\s\S])*?\bsign\w*\b[^.]{0,30}\bout\b|\bsign\w*\b[^.]{0,30}\bout\b(?:(?!\n\s*\n|\n- )[\s\S])*?e-?mail)
