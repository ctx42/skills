---
type: regex
target: {source: file, path: tmp/export-plan.md}
flags: "i"
---
(depend\w*|block\w*|requires?|needs?|after|once|until|first|cannot start|can only|using|uses|builds? on)[^\n]{0,120}(item\s*#?\d|#\d|\bsplit|per[- ]entity|own file)
