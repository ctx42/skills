---
tags: [case:style--delegated-by-review, skill:style, skill:review, sec:style:usage, sec:style:production, sec:style:test, sec:style:self-learning, ref:style/checking, sec:review:working-diff-injected, sec:review:check-mode, sec:review:self-learning, needs-shell]
runs: 1
max_turns: 50
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, LSP, Write, Edit, Bash(git:*)]
append_system_prompt: |
  The user writes English; reply in English.
---

/go:review
