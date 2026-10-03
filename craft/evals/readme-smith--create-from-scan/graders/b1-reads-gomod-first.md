---
type: tool_order
before: {tool: Read, input_match: '"file_path":"[^"]*go\.mod"'}
after: {tool: Write, input_match: '"file_path":"[^"]*README\.md"'}
---
