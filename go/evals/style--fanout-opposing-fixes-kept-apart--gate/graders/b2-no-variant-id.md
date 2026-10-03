---
type: regex
target: last_message
match: not_contains
---
`(?!(?:separate-distinct-topics)`)(?=[a-z0-9-]*(?:topic|blank))[a-z0-9]+(?:-[a-z0-9]+)+`
