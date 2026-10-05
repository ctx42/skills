---
tags: [case:fix-all--answered-round-then-unattended, skill:fix-all, needs-shell, sec:fix-all:usage, sec:fix-all:1-triage-before-any-edit, sec:fix-all:2-fix-one-commit-per-fix, sec:fix-all:3-report]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Edit, Write, Bash(git:*), Bash(go:*)]
append_system_prompt: |
  The user writes English; reply in English.

  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.

  1. Leave #2 as it is; do not fix it.
---

/craft:fix-all
