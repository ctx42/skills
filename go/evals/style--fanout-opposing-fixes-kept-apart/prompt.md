---
tags: [case:style--fanout-opposing-fixes-kept-apart, skill:style, sec:style:usage, sec:style:production, sec:style:test, sec:style:self-learning, ref:style/checking, needs-shell]
runs: 1
max_turns: 80
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, LSP, Write, Edit, Agent, Task, Bash(go test:*)]
append_system_prompt: |
  The user writes English; reply in English.
  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.

  1. Apply all of them. If the go test gate cannot run here, apply them
     anyway; I will run the tests myself.
---

/go:style ./... max_issues=25 depth=standard
