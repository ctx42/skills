---
tags: [case:review--walk-records-only-confirmed-findings--gate, skill:review, sec:review:boundaries, sec:review:sources-of-truth, sec:review:modes, ref:create/project-config, sec:review:severity, sec:review:category, sec:review:review-file-format, ref:review/review-file, sec:review:usage, sec:review:documentation-corpus, ref:create/authoring-guide, ref:create/doc-corpus, ref:create/errata, ref:create/srd-procedures, sec:review:walk]
runs: 1
max_turns: 40
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/srd:review specs/login.md walk
