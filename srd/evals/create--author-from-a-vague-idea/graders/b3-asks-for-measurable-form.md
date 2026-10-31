---
type: regex
target: trace
flags: "i"
---
\{"type":"assistant"[^\n]*(?:"type":"text","text":"[^\n]*timel[^\n]*\?|"type":"thinking","thinking":"(?:[^"\\]|\\.)*(?:\b(?:ask|clarif|flag)(?:[^"\\]|\\.)*timel|timel(?:[^"\\]|\\.)*\b(?:defin|measur|concret|clarif)))
