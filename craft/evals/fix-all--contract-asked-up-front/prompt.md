---
tags: [case:fix-all--contract-asked-up-front, skill:fix-all, needs-shell, sec:fix-all:usage, sec:fix-all:1-triage-before-any-edit, sec:fix-all:2-fix-one-commit-per-fix, sec:fix-all:3-report]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Edit, Write, Bash(git:*), Bash(go:*)]
append_system_prompt: |
  The user writes English; reply in English.
---

/craft:fix-all
