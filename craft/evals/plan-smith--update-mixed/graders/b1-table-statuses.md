---
type: regex
target: {source: file, path: sso-plan.md}
flags: "m"
---
^(?=[\s\S]*^\| 1 +\| Provider config +\| N +\|$)(?=[\s\S]*^\| 2 +\| Login flow +\| Y +\|$)(?=[\s\S]*^\| 3 +\| Session storage +\| Y +\|$)(?=[\s\S]*^\| 4 +\| Operator docs +\| X +\|$)
