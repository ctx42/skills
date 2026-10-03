---
type: regex
target: {source: file, path: initiatives/audit-log-retention/srd.md}
match: not_contains
flags: "m"
---
^## Glossary\b(?:(?!^## )[\s\S])*?^(#{3,4}\s*|\*\*|[-*]\s+\*\*)Retention Period\b(?:(?!^#)[\s\S])*?(\bMUST\b|\bSHALL\b|\bSHOULD\b|\bMAY\b|\d)
