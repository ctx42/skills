---
type: regex
target: {source: file, path: craft/skills/foo/SKILL.md}
match: "not_contains"
flags: "m"
---
^.{81,}$
