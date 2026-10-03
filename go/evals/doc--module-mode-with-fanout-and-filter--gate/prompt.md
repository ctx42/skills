---
tags: [case:doc--module-mode-with-fanout-and-filter--gate, skill:doc, sec:doc:usage, sec:doc:target, sec:doc:the-checklist, sec:doc:accuracy, sec:doc:per-item-loop, sec:doc:output, sec:style:production, sec:doc:plan-file-package-module, sec:doc:controls, sec:doc:verify]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, LSP, Agent, Bash(go:*), Bash(gofmt:*)]
append_system_prompt: |
  The user writes English; reply in English.
---

/go:doc module fanout packages=svc,api
