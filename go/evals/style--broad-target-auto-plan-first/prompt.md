---
tags: [case:style--broad-target-auto-plan-first, skill:style, sec:style:usage, sec:style:production, sec:style:test, sec:style:self-learning, ref:style/checking]
runs: 1
max_turns: 30
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, LSP, Write, Edit, Agent, Task]
append_system_prompt: |
  The user writes English; reply in English.
---

/go:style ./...
