---
tags: [case:cover--deferred-and-uncoverable-are-reported--include-all, skill:cover, sec:cover:target, sec:cover:per-function-loop, sec:cover:classify-each-uncovered-line, sec:cover:write, sec:cover:verify, sec:cover:output, sec:cover:plan-file-package-module, sec:cover:un-coverable-categories, sec:cover:controls, skill:style, sec:style:test, sec:style:production, needs-shell]
runs: 1
max_turns: 80
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash(go:*), Bash(gofmt:*), Bash(mkdir:*), Bash(awk:*), Bash(rm:*)]
append_system_prompt: |
  The user writes English; reply in English.
  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.
  Before taking a scripted answer, write out in full, as your reply text, the
  message you would send the user at that point.

  1. Approved. Go ahead with the plan as proposed.
---

/go:cover ./pkg/net include=all
