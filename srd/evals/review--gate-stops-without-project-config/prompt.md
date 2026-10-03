---
tags: [case:review--gate-stops-without-project-config, skill:review, sec:review:modes, sec:review:sources-of-truth, ref:create/project-config]
runs: 1
max_turns: 15
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/srd:review specs/login.md
