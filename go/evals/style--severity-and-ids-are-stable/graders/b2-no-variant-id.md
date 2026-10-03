---
type: regex
target: last_message
match: not_contains
---
`(?!(?:receivers-three-letter-type|every-exported-symbol)`)(?=[a-z0-9-]*(?:receiver|godoc|doc))[a-z0-9]+(?:-[a-z0-9]+)+`
