---
type: regex
target: {source: file, path: craft/skills/plan-smith/SKILL.md}
flags: "i"
---
reject[^\n]*(?:\n[^\n]*)?\bX\b[\s\S]{0,300}?(?:never|not|keep)[^\n]*(?:\n[^\n]*)?\b(?:delete|row)|\bX\b[^\n]*(?:\n[^\n]*)?reject[\s\S]{0,300}?(?:delete|row)
