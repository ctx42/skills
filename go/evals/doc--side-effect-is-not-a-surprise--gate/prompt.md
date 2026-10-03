---
tags: [case:doc--side-effect-is-not-a-surprise--gate, skill:doc, sec:doc:usage, sec:doc:target, sec:doc:the-checklist, sec:doc:accuracy, sec:doc:per-item-loop, sec:doc:output, sec:style:production, sec:doc:plan-file-package-module]
runs: 1
max_turns: 40
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, LSP, Bash(go:*), Bash(gofmt:*)]
append_system_prompt: |
  The user writes English; reply in English.
---

/go:doc ./pkg/sink
