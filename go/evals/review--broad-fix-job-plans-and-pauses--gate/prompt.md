---
tags: [case:review--broad-fix-job-plans-and-pauses--gate, skill:review, sec:review:usage, sec:review:working-diff-injected, sec:review:check-mode, ref:style/checking, sec:style:production, sec:style:test, ref:review/fixing]
runs: 1
max_turns: 50
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash(git:*), Bash(go:*)]
append_system_prompt: |
  The user writes English; reply in English.
---

/go:review ./... fix
