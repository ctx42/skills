---
tags: [case:style--production-rules-while-writing, skill:style, sec:style:production, sec:style:self-learning]
runs: 1
max_turns: 30
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, LSP, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
  This project's Go conventions live in the go:style skill; load it
  before editing any .go file.
---

Add a Close method to the Service type in service.go
