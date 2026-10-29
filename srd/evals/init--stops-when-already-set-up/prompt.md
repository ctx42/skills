---
tags: [case:init--stops-when-already-set-up, skill:init, sec:init:usage, sec:init:boundaries, sec:init:sources-of-truth, sec:init:run, sec:init:finding-values, sec:init:key-reference, sec:init:report, sec:init:self-learning, ref:create/project-config]
runs: 1
max_turns: 30
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/srd:init
