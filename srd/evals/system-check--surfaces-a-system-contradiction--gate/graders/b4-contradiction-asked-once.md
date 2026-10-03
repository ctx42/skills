---
type: regex
target: {source: file, path: specs/labeling.questions.md}
match: "count:1"
flags: "i"
---
\*\*Q\d+\*\*(?:(?!\*\*Q\d)[\s\S])*?comma
