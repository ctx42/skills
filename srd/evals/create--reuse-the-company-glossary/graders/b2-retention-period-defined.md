---
type: regex
target: {source: file, path: initiatives/audit-log-retention/srd.md}
flags: "m"
---
^## Glossary\b(?:(?!^## )[\s\S])*^(#{3,4}\s*|\*\*|[-*]\s+\*\*)Retention Period\b
