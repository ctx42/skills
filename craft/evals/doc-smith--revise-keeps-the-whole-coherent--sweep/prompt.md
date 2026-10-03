---
tags: [case:doc-smith--revise-keeps-the-whole-coherent--sweep, skill:doc-smith, sec:doc-smith:usage, sec:doc-smith:whole-document-pass-all-modes, sec:doc-smith:self-learning, ref:doc-smith/writing-guide, sec:doc-smith:revise-mode, sec:doc-smith:technical-claims-flag-don-t-fix]
runs: 1
max_turns: 40
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/craft:doc-smith Sweep them all to project now.
