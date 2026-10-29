---
type: regex
target: {source: file, path: tmp/sso-plan.md}
flags: "im"
---
^(?=[\s\S]*^## \d+\.[^\n]*(?:(provider|config)))(?=[\s\S]*^## \d+\.[^\n]*(?:login))(?=[\s\S]*^## \d+\.[^\n]*(?:session))(?=[\s\S]*^## \d+\.[^\n]*(?:doc))
