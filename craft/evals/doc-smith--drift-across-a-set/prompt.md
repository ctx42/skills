---
tags: [case:doc-smith--drift-across-a-set, skill:doc-smith, sec:doc-smith:usage, sec:doc-smith:whole-document-pass-all-modes, sec:doc-smith:self-learning, ref:doc-smith/writing-guide, sec:doc-smith:audit-mode, sec:doc-smith:technical-claims-flag-don-t-fix]
runs: 1
max_turns: 40
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/craft:doc-smith audit docs/install.md docs/config.md docs/usage.md as one manual
