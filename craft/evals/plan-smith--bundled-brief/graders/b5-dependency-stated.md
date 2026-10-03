---
type: regex
target: {source: file, path: tmp/export-plan.md}
flags: "i"
---
(depend\w*|block\w*|requires?|needs?|after|once|until|first|cannot start|can only|using|uses|builds? on|from|with)[^\n]{0,120}(item\s*#?\d|#\d|\bsplit|per[- ]entity|own file)|(item\s*#?\d|#\d)[^\n]{0,40}(depends?|is blocked|needs|requires)
