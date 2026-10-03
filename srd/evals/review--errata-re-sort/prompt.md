---
tags: [case:review--errata-re-sort, skill:review, sec:review:boundaries, sec:review:sources-of-truth, sec:review:modes, ref:create/project-config, sec:review:severity, sec:review:category, sec:review:review-file-format, ref:review/review-file, sec:review:errata, ref:create/errata]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/srd:review specs/login.md errata, then the same command again
