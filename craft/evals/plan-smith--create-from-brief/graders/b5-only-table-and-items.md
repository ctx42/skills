---
type: regex
target: {source: file, path: tmp/sso-plan.md}
match: "not_contains"
flags: "im"
---
^#{2,6} (?!Summary$|\d+\. )|^\**(assumptions?|open (questions?|choices|decisions)|risks?|decisions?)\**:?\s*$
