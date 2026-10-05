---
tags: [case:review--review-the-current-diff, skill:review, sec:review:usage, sec:review:working-diff-injected, sec:review:check-mode, ref:style/checking, sec:style:production, needs-shell]
runs: 1
max_turns: 40
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Bash(git:*)]
append_system_prompt: |
  The user writes English; reply in English.
---

/go:review
