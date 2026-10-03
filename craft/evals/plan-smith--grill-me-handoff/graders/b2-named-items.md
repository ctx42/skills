---
type: regex
target: {source: file, path: tmp/csv-export-plan.md}
flags: "im"
---
^(?=[\s\S]*^## \d+\.[^\n]*(?:scope|filter))(?=[\s\S]*^## \d+\.[^\n]*(?:limit|size|row))(?=[\s\S]*^## \d+\.[^\n]*(?:format|csv|4180))(?=[\s\S]*^## \d+\.[^\n]*(?:deliver|download))(?=[\s\S]*^## \d+\.[^\n]*(?:permission|access))(?=[\s\S]*^## \d+\.[^\n]*(?:audit))
