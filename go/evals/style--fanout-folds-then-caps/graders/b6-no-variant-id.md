---
type: regex
target: last_message
match: not_contains
---
`(?!(?:wrap-errors-w|receivers-three-letter-type|every-exported-symbol|separate-distinct-topics)`)(?=[a-z0-9-]*(?:receiver|exported|topic|blank))[a-z0-9]+(?:-[a-z0-9]+)+`
