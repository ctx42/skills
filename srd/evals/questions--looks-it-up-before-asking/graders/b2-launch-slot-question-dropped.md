---
type: regex
target: {source: file, path: initiatives/part-kit-tracking/srd.questions.md}
match: not_contains
flags: "i"
---
\*\*Q\d+\*\*(?=(?:(?!\*\*Q\d)[\s\S])*Launch Slot)(?=(?:(?!\*\*Q\d)[\s\S])*(defin|\bterm\b|glossar))
