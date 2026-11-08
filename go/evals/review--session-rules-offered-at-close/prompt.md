---
tags: [case:review--session-rules-offered-at-close, skill:review, sec:review:usage, sec:review:check-mode, ref:style/checking, ref:style/production, needs-shell]
runs: 1
max_turns: 40
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash(git:*)]
append_system_prompt: |
  The user writes English; reply in English.
---

/go:review
