---
tags: [case:edit--corpus-grounded-edit-routes-the-unconfirmable, skill:edit, sec:edit:usage, sec:edit:boundaries, sec:edit:sources-of-truth, sec:edit:session-start-every-mode, sec:edit:edit-discipline, sec:edit:modes, sec:edit:session-end-every-mode, sec:edit:self-learning, ref:create/project-config, ref:create/doc-corpus, ref:create/authoring-guide, sec:edit:decision-log, ref:edit/decision-log, sec:edit:documentation-corpus, ref:edit/corpus-edits, skill:report-doc-gap, skill:kb]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
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
  1. If the skill asks what to change in GR-2, or proposes GR-2 with a placeholder for the retry count: "The gateway retries a failed token check three times — that is what it does today. Make GR-2 say so."
  2. To a proposal for GR-2 that states three retries: "YN".
  3. To an offer to file or work documentation gaps: "File it."
  4. Anything else: "That's all — close the session."
---

/srd:edit specs/login.md GR-2
