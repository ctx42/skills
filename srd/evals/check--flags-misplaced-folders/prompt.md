---
tags: [case:check--flags-misplaced-folders, skill:check, sec:check:usage, sec:check:boundaries, sec:check:sources-of-truth, sec:check:run, sec:check:report, sec:check:self-learning, ref:create/project-config]
runs: 1
max_turns: 30
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/srd:check
