---
type: regex
target: {source: file, path: specs/labeling.questions.md}
flags: "i"
---
\*\*Q\d+\*\*(?:(?!\*\*Q\d)[\s\S])*GR-7(?:(?!\*\*Q\d)[\s\S])*fast
