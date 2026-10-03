---
type: regex
target: {source: file, path: specs/labeling.questions.md}
match: not_contains
flags: "i"
---
\*\*Q\d+\*\*(?=(?:(?!\*\*Q\d)[\s\S])*Namespace)(?=(?:(?!\*\*Q\d)[\s\S])*(defin|\bterm\b|glossar))
