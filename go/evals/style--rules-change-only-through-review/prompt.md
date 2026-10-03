---
tags: [case:style--rules-change-only-through-review, skill:style, sec:style:usage, ref:style/checking, sec:style:self-learning]
runs: 1
max_turns: 20
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, LSP, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/go:style add a rule that test helpers never return errors
