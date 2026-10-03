---
type: regex
target: {source: file, path: specs/labeling.questions.md}
match: not_contains
flags: "im"
---
^(?!\s*<!--)[^\n]*(#\d|\b(REQ|SCO|GLO|LANG|STR|STA)-\d|\[(blocker|major|minor)|SRD:)
