---
tags: [case:edit--decision-log-written-per-edit, skill:edit, sec:edit:usage, sec:edit:boundaries, sec:edit:sources-of-truth, sec:edit:session-start-every-mode, sec:edit:edit-discipline, sec:edit:modes, sec:edit:session-end-every-mode, sec:edit:self-learning, ref:create/project-config, ref:create/doc-corpus, ref:create/authoring-guide, sec:edit:decision-log, ref:edit/decision-log, ref:create/srd-procedures, sec:edit:id-rules, ref:edit/id-rules]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.
  Before taking a scripted answer, write out in full, as your reply text, the
  message you would send the user at that point (every proposal with its
  location, before/after text and choices), then write the answer you take on a
  line of its own as `User: <answer>`, and only then continue. Never apply a
  change whose proposal you have not written out this way.

  Scripted answers (pick the one that fits the question):
  1. To the first proposal: "Y — retention isn't ours, drop it".
  2. When the skill says the entry has nothing further or asks how to go on, the first time: "Next entry."
  3. To the next proposal: "S".
  4. After that, whenever the skill asks how to go on or proposes anything: "That's all — close the session."
---

/srd:edit specs/login.md
