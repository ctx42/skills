---
tags: [case:plan-smith--write-from-brief, skill:plan-smith, sec:plan-smith:usage, sec:plan-smith:self-learning, sec:plan-smith:format, sec:plan-smith:summary, sec:plan-smith:1-item-name-x, sec:plan-smith:3-item-name-x-rejected-one-line-reason, sec:plan-smith:n-remove-this-plan, sec:plan-smith:write-mode]
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

  1. Those choices are not made yet — leave them open and write the plan now.
---

/craft:plan-smith write plan the work to add SSO: provider config, login flow, session storage, and a page in the operator docs.
