---
tags: [case:style--severity-and-ids-are-stable, skill:style, sec:style:usage, sec:style:production, sec:style:test, sec:style:self-learning, ref:style/checking]
runs: 1
max_turns: 40
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, LSP, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/go:style ./...
