---
type: regex
target: {source: file, path: specs/login.decisions.md}
match: not_contains
flags: "s"
---
LCK-1|\bmust\b.{0,40}MUST
