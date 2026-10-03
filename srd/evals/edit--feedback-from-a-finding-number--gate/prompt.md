---
tags: [case:edit--feedback-from-a-finding-number--gate, skill:edit, sec:edit:usage, sec:edit:boundaries, sec:edit:sources-of-truth, sec:edit:session-start-every-mode, sec:edit:edit-discipline, sec:edit:modes, sec:edit:session-end-every-mode, sec:edit:self-learning, ref:create/project-config, ref:create/doc-corpus, ref:create/authoring-guide, ref:review/review-file, sec:edit:decision-log, ref:edit/decision-log]
runs: 1
max_turns: 30
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

/srd:edit specs/login.md #2
