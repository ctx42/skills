---
tags: [case:grill-me--caller-supplied-subject--gate, skill:grill-me, sec:grill-me:usage, sec:grill-me:how-it-works, sec:grill-me:rules, sec:grill-me:self-learning]
runs: 1
max_turns: 20
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: |
  The user writes English; reply in English.
---

/craft:grill-me the docs don't say what happens to an in-flight order when a station goes offline
