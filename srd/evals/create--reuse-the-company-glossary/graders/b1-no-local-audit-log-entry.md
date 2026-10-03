---
type: regex
target: {source: file, path: initiatives/audit-log-retention/srd.md}
match: not_contains
flags: "mi"
---
^## Glossary\b(?:(?!^## )[\s\S])*?^(#{3,4}\s*|\*\*|[-*]\s+\*\*)Audit Log\b
