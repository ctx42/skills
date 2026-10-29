---
type: regex
target: last_message
match: "not_contains"
flags: "im"
---
^[-*\s]*(?:\*\*[^*\n]*\*\*:?\s*)?(?:should|do|does|is|are|what|which|how|can|will)\b[^\n?]{0,40}(filtered view|whole dataset|100k|100,000|row limit|BOM|4180|encoding|synchronous|background job|email|403|viewer|grant|audit row)[^\n?]*\?
