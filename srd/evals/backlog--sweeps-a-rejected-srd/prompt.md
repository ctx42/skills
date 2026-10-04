---
tags: [case:backlog--sweeps-a-rejected-srd, skill:backlog, sec:backlog:usage, sec:backlog:boundaries, sec:backlog:sources-of-truth, sec:backlog:backends, sec:backlog:workflow, ref:create/project-config, ref:create/doc-corpus, skill:report-doc-gap, sec:report-doc-gap:the-gap-tools, sec:report-doc-gap:the-gap-record, sec:report-doc-gap:workflow]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/srd:backlog
