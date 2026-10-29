---
tags: [case:init--adds-srd-keys-to-a-starter-config, skill:init, sec:init:usage, sec:init:boundaries, sec:init:sources-of-truth, sec:init:run, sec:init:finding-values, sec:init:key-reference, sec:init:report, sec:init:self-learning, ref:create/project-config]
runs: 1
max_turns: 30
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.

  Scripted answers (pick the one that fits the question):
  1. To the proposed project-config.md: "yes".
  2. Anything else: "That's all."
---

/srd:init
