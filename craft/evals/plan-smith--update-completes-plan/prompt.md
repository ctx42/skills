---
tags: [case:plan-smith--update-completes-plan, skill:plan-smith, sec:plan-smith:usage, sec:plan-smith:self-learning, sec:plan-smith:format, sec:plan-smith:summary, sec:plan-smith:1-item-name-x, sec:plan-smith:3-item-name-x-rejected-one-line-reason, sec:plan-smith:n-remove-this-plan, sec:plan-smith:update-mode]
runs: 1
max_turns: 40
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.

  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.
  Before taking a scripted answer, write out in full, as your reply text, the
  message you would send the user at that point.

  1. No, keep it.
---

/craft:plan-smith update tmp/done-plan.md
