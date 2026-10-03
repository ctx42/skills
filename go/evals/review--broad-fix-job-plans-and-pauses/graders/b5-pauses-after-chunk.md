---
type: regex
target: trace
flags: "i"
---
chunk[^\"]{0,400}(go ahead|go-ahead|continue|proceed|next chunk)[^\"]{0,40}\?
