---
tags: [case:doc-smith--create-grounded-manual--gate, skill:doc-smith, sec:doc-smith:usage, sec:doc-smith:whole-document-pass-all-modes, sec:doc-smith:self-learning, ref:doc-smith/writing-guide, sec:doc-smith:create-mode]
runs: 1
max_turns: 40
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/craft:doc-smith create a user manual for the billing dashboard
