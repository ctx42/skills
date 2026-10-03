---
tags: [case:style--fix-applies-everything-behind-a-green-gate, skill:style, sec:style:usage, sec:style:production, sec:style:test, sec:style:self-learning, ref:style/checking, needs-shell]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, LSP, Write, Edit, Bash(go test:*), Bash(go:*)]
append_system_prompt: |
  The user writes English; reply in English.
---

/go:style ./pkg/foo fix
