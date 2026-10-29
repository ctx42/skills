---
tags: [case:doc-edit--resolves-a-gap-in-the-edited-document, skill:doc-edit, sec:doc-edit:usage, sec:doc-edit:boundaries, sec:doc-edit:sources-of-truth, sec:doc-edit:session-start, sec:doc-edit:edit-loop, sec:doc-edit:facts, sec:doc-edit:document-kinds, sec:doc-edit:session-end, ref:create/project-config, ref:create/doc-corpus, sec:doc-edit:resolving-a-gap]
runs: 1
max_turns: 50
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.

  Scripted answers (pick the one that fits the question):
  1. To a proposal that adds the 10-working-day payout deadline: "Y".
  2. Anything else: "That's all — close the session."
---

/srd:doc-edit docs/operations/scrub-refunds.md add the payout deadline: a scrub refund is paid out within 10 working days of the scrub
