---
type: regex
target: last_message
flags: "i"
---
(tools?|ran|shell)[^\n]{0,120}(none|nothing|no (gofmt|go vet|vet|lint|tests?|shell|commands?)|LSP|grep|Read|awk)
