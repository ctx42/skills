---
tags: [case:style--fanout-opposing-fixes-kept-apart--gate, skill:style, sec:style:usage, sec:style:production, sec:style:test, sec:style:self-learning, ref:style/checking]
runs: 1
max_turns: 80
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, LSP, Write, Edit, Agent, Task]
append_system_prompt: |
  The user writes English; reply in English.
---

/go:style ./... max_issues=25 depth=standard
