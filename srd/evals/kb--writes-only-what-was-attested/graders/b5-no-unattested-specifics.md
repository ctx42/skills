---
type: regex
target: {source: file, path: kb/_inbox.md}
match: not_contains
flags: "i"
---
\b(retain|retention|expir|delet|purg|archiv|limit|maximum|at most|up to \d|\d+\s*(hours?|days?|weeks?|months?|years?)|dismissed|closed|resolved)\b
