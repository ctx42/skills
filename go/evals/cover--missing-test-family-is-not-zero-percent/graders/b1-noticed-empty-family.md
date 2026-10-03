---
type: regex
target: trace
flags: "i"
---
\{"type":"assistant"[^\n]*"type":"text","text":"[^\n]*(no tests to run|matche[sd] no|no (direct|matching|Test_Normalize)[^"]{0,40}tests?|empty (test )?family|family (was|is) empty|no tests? match(es|ed)?|no Test_Normalize)
