---
type: regex
target: {source: file, path: tmp/agent-plan-csv-export.md}
flags: "i"
---
^(?=[\s\S]*exactly\s+the\s+filtered\s+rows)(?=[\s\S]*100,001)(?=[\s\S]*Excel[\s\S]*(round-trip|round\s+trip|parser))(?=[\s\S]*job\s+row)(?=[\s\S]*\b403\b)(?=[\s\S]*(exactly\s+)?one\s+audit\s+row)
