---
type: regex
target: {source: file, path: tmp/agent-plan-sso.md}
flags: "im"
---
^(?=[\s\S]*^## \d+\.[^\n]*(?:(provider|config)))(?=[\s\S]*^## \d+\.[^\n]*(?:login))(?=[\s\S]*^## \d+\.[^\n]*(?:session))(?=[\s\S]*^## \d+\.[^\n]*(?:doc))
