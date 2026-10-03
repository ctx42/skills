---
tags: [case:review--feedback-export-for-a-ticket, skill:review, sec:review:boundaries, sec:review:sources-of-truth, sec:review:modes, ref:create/project-config, sec:review:feedback, ref:review/review-file]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

/srd:review specs/login.md feedback
