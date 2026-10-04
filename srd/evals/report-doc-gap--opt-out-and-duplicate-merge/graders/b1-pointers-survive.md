---
type: regex
target: mock_calls
flags: "m"
match: not_contains
---
^(?=[^\n]*"tool":"[^"]*update_gap")(?![^\n]*"doc_id":"docs/api-gateway/overview\.md"[^\n]*)|^(?=[^\n]*"tool":"[^"]*update_gap")(?![^\n]*"source_url":"https://docs\.example\.com/api-gateway/overview#upstream-calls")|^(?=[^\n]*"tool":"[^"]*update_gap")(?![^\n]*"heading_path":\["API Gateway","Upstream calls"\])
