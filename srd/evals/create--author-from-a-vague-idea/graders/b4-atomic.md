---
type: regex
target: {source: file, path: initiatives/password-reset/srd.md}
match: not_contains
flags: "i"
---
\*\*[A-Z]+-\d+[a-z]?:\*\*(?:(?!\*\*[A-Z]+-\d)[\s\S])*?(e-?mail(?:(?!\*\*[A-Z]+-\d)[\s\S])*?\bsign\w*\b[^.]{0,30}\bout\b|\bsign\w*\b[^.]{0,30}\bout\b(?:(?!\*\*[A-Z]+-\d)[\s\S])*?e-?mail)
