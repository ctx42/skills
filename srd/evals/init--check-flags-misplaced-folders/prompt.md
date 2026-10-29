---
tags: [case:init--check-flags-misplaced-folders, skill:init, sec:init:usage, sec:init:boundaries, sec:init:sources-of-truth, sec:init:run, sec:init:check-mode, sec:init:self-learning, ref:create/project-config]
runs: 1
max_turns: 30
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/srd:init check
