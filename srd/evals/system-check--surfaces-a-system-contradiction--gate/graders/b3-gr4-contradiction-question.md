---
type: regex
target: {source: file, path: specs/labeling.questions.md}
flags: "i"
---
\*\*Q\d+\*\*(?:(?!\*\*Q\d)[\s\S])*GR-4(?:(?!\*\*Q\d)[\s\S])*comma
