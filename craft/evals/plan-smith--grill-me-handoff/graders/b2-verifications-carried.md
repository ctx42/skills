---
type: regex
target: {source: file, path: tmp/csv-export-plan.md}
flags: "i"
---
^(?=[\s\S]*exactly the filtered rows)(?=[\s\S]*100,001)(?=[\s\S]*Excel[\s\S]*(round-trip|round trip|parser))(?=[\s\S]*job row)(?=[\s\S]*\b403\b)(?=[\s\S]*(exactly )?one audit row)
