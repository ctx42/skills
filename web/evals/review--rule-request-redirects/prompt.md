---
tags: [case:review--rule-request-redirects, skill:review, sec:review:usage]
runs: 1
max_turns: 20
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/web:review add "never export a default from a .ts module"
