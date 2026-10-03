---
tags: [case:doc--side-effect-is-not-a-surprise, skill:doc, sec:doc:usage, sec:doc:target, sec:doc:the-checklist, sec:doc:accuracy, sec:doc:per-item-loop, sec:doc:output, sec:style:production, sec:doc:plan-file-package-module, needs-shell]
runs: 1
max_turns: 40
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, LSP, Bash(go:*), Bash(gofmt:*)]
append_system_prompt: |
  The user writes English; reply in English.
  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.

  1. To the plan: "Approved, go ahead."
---

/go:doc ./pkg/sink
