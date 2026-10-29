---
type: regex
target: last_message
---
(?:\b[0-9a-f]{7,40}\b[^\n]{0,20}\n?(?:```[a-z]*\n)?[a-z]+(\([^)\n]+\))?!?: [\s\S]*?){3}
