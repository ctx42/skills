---
type: regex
target: last_message
match: "not_contains"
flags: "im"
---
^\s*(?:#+\s*|\*\*)(summary|recap|key findings|overview of findings)\b|\b(in summary|to summari[sz]e|in short)\b
