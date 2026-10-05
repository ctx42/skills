---
tags: [case:fix-all--all-auto-commits-separately, skill:fix-all, needs-shell, sec:fix-all:usage, sec:fix-all:1-triage-before-any-edit, sec:fix-all:2-fix-one-commit-per-fix, sec:fix-all:3-report]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Edit, Write, Bash(git:*), Bash(go:*)]
append_system_prompt: |
  The user writes English; reply in English.

  Attribution for git commits you create from here on:
  - End git commit messages with:
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
---

/craft:fix-all
