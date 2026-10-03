---
tags: [case:create--start-costs-nothing-before-the-interview--gate, skill:create, sec:create:usage, sec:create:documentation-corpus, sec:create:workflow, ref:create/project-config, ref:create/doc-corpus]
runs: 1
max_turns: 30
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/srd:create a rate limit for the export API
