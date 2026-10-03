---
tags: [case:plan-smith--ambiguous-request, skill:plan-smith, sec:plan-smith:usage, sec:plan-smith:self-learning]
runs: 1
max_turns: 20
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/craft:plan-smith the SSO plan
