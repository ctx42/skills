---
type: regex
target: {source: file, path: README.md}
match: "not_contains"
flags: "i"
---
sandbox|this environment|could not be (run|verified)|not (been )?verified|unverified|untested
