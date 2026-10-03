---
type: regex
target: {source: file, path: tmp/export-plan.md}
flags: "im"
---
^(?=[\s\S]*^## \d+\.[^\n]*(disk|stor|split|entit|location|off the app|destination|move))(?=[\s\S]*^## \d+\.[^\n]*(notif|alert|fail))(?=[\s\S]*^## \d+\.[^\n]*(reconcil|tie|dashboard|match|finance|figures|numbers))
