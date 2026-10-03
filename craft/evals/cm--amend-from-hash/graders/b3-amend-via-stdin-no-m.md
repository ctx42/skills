---
type: tool_used
tool: Bash
input_match: '(?:\b|\\n)git\s+commit\b(?=(?:[^"\\]|\\.)*--amend)(?=(?:[^"\\]|\\.)*(-F\s*-|--file[= ]-))(?!(?:[^"\\]|\\.)*\s-m\b)'
min: 1
---
