---
type: regex
target: {source: file, path: initiatives/password-reset/srd.md}
match: not_contains
flags: "m"
---
^## (Scope|Requirements)\b[\s\S]*^## Glossary\b
