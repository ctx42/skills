---
tags: [case:review--check-a-prior-review, skill:review, sec:review:boundaries, sec:review:sources-of-truth, sec:review:modes, ref:create/project-config, sec:review:severity, sec:review:category, sec:review:review-file-format, ref:review/review-file, sec:review:check]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

/srd:review specs/login.md check
