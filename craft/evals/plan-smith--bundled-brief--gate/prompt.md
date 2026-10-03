---
tags: [case:plan-smith--bundled-brief--gate, skill:plan-smith, sec:plan-smith:usage, sec:plan-smith:self-learning, sec:plan-smith:format, sec:plan-smith:summary, sec:plan-smith:1-item-name-x, sec:plan-smith:3-item-name-x-rejected-one-line-reason, sec:plan-smith:n-remove-this-plan, sec:plan-smith:write-mode]
runs: 1
max_turns: 30
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/craft:plan-smith we need to get the nightly export working properly — right now it dumps everything to one CSV on the app server, which fills the disk, nobody is told when it fails, and finance says the numbers do not tie out with the dashboard. The figures can only be reconciled once the export is split per entity, since today there is nothing to compare line by line. Write that up as a plan.
