---
tags: [case:doc-edit--hands-an-srd-to-edit, skill:doc-edit, sec:doc-edit:usage, sec:doc-edit:boundaries, sec:doc-edit:sources-of-truth, sec:doc-edit:session-start, sec:doc-edit:edit-loop, sec:doc-edit:facts, sec:doc-edit:document-kinds, sec:doc-edit:session-end, ref:create/project-config, ref:create/doc-corpus, skill:edit]
runs: 1
max_turns: 30
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/srd:doc-edit initiatives/autoco/srd.md tighten the wording of AC-2
