---
tags: [case:create--author-from-a-vague-idea--gate, skill:create, sec:create:usage, sec:create:workflow, ref:create/project-config]
runs: 1
max_turns: 30
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/srd:create — we need an SRD for a password reset feature
