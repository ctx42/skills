---
type: tool_order
before: {tool: mcp__srd__list_gaps, input_match: '"status":"open"'}
after: {tool: Edit, input_match: '"file_path":"[^"]*correlation\.md"'}
---
