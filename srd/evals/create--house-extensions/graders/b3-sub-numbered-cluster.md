---
type: regex
target: {source: file, path: initiatives/leak-severity/srd.md}
---
\*\*([A-Z]+-\d+)a:\*\*[^\n]*High[\s\S]*\*\*\1b:\*\*[^\n]*Medium[\s\S]*\*\*\1c:\*\*[^\n]*Low
