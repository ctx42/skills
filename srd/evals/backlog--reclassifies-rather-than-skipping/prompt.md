---
tags: [case:backlog--reclassifies-rather-than-skipping, skill:backlog, sec:backlog:usage, sec:backlog:boundaries, sec:backlog:sources-of-truth, sec:backlog:backends, sec:backlog:workflow, ref:create/project-config, sec:kb:boundaries, sec:kb:the-kb-folder, sec:kb:invocation, sec:kb:workflow, sec:kb:page-anatomy, sec:kb:open-questions, sec:kb:output]
runs: 1
max_turns: 50
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.
  Before taking a scripted answer, write out in full, as your reply text, the
  message you would send the user at that point.

  1. To the battery-low threshold question: "Actually nobody knows that yet — no one has measured it on the current cells."
  2. To any offer of another list: "No, that's all for today."
---

/srd:backlog deferred
