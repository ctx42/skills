---
tags: [case:review--broad-target-auto-plan-first, skill:review, sec:review:usage, sec:review:working-diff-injected, sec:review:check-mode, ref:style/checking, sec:style:production, fan-out]
runs: 1
max_turns: 80
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Agent, Bash(git:*)]
append_system_prompt: |
  The user writes English; reply in English.
  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.
  Before taking a scripted answer, write out in full, as your reply text, the
  message you would send the user at that point.

  1. go ahead, those defaults are fine
---

/go:review ./...
