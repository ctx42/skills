---
tags: [case:review--broad-target-auto-plan-first--gate, skill:review, sec:review:usage, sec:review:working-diff-injected, sec:review:check-mode, ref:style/checking, sec:style:production]
runs: 1
max_turns: 30
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill, Agent, Bash(git:*)]
append_system_prompt: |
  The user writes English; reply in English.
---

/go:review ./...
