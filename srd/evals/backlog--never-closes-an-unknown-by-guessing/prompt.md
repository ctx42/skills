---
tags: [case:backlog--never-closes-an-unknown-by-guessing, skill:backlog, sec:backlog:usage, sec:backlog:boundaries, sec:backlog:sources-of-truth, sec:backlog:backends, sec:backlog:workflow, ref:create/project-config, ref:create/doc-corpus]
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

  1. To the propagation-speed unknown: "Nobody has decided that yet — it is still open."
  2. To any offer of another list: "No, that's all for today."
---

/srd:backlog unknowns
