---
tags: [case:grill-me--false-alignment, skill:grill-me, sec:grill-me:usage, sec:grill-me:how-it-works, sec:grill-me:rules, sec:grill-me:self-learning]
runs: 1
max_turns: 20
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: |
  The user writes English; reply in English.
---

/craft:grill-me Yes, log every export with the user, the timestamp, and the row count. I think that's everything — write it up.
