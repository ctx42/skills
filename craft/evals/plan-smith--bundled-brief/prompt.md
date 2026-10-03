---
tags: [case:plan-smith--bundled-brief, skill:plan-smith, sec:plan-smith:usage, sec:plan-smith:self-learning, sec:plan-smith:format, sec:plan-smith:summary, sec:plan-smith:1-item-name-x, sec:plan-smith:3-item-name-x-rejected-one-line-reason, sec:plan-smith:n-remove-this-plan, sec:plan-smith:write-mode]
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

  1. 'Not tying out' means the per-entity daily totals in the export differ from the dashboard's totals for the same day. The files should go to the shared object store (s3://finance-exports) instead of the app server's disk, and failure notices go to the #data-alerts channel. Save the plan as tmp/export-plan.md.
---

/craft:plan-smith we need to get the nightly export working properly — right now it dumps everything to one CSV on the app server, which fills the disk, nobody is told when it fails, and finance says the numbers do not tie out with the dashboard. The figures can only be reconciled once the export is split per entity, since today there is nothing to compare line by line. Write that up as a plan.
