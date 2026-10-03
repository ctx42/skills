---
type: tool_order
before: {tool: Read, input_match: '"file_path":"[^"]*\.github/workflows/ci\.yml"'}
after: {tool: Write, input_match: '"file_path":"[^"]*README\.md"'}
---
