---
tags: [case:questions--surfaces-a-system-contradiction, skill:questions, sec:questions:boundaries, sec:questions:support-files, sec:questions:documentation-corpus, sec:questions:invocation, sec:questions:review-default, sec:questions:questions-file, sec:questions:walk, skill:review, sec:review:boundaries, sec:review:sources-of-truth, sec:review:documentation-corpus, sec:review:severity-and-category, ref:review/finding-tags, sec:review:modes, sec:review:review-file-format, sec:review:review-default, ref:review/review-file, ref:create/authoring-guide, ref:create/errata, ref:create/srd-procedures, ref:create/project-config, ref:create/doc-corpus]
runs: 1
max_turns: 80
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

  Scripted answers (pick the one that fits):
  1. To any offer about draft documentation gaps: "Keep them as drafts for
     later."
  2. To the first question you put, if it is about KIT-7's lookup speed: "300
     ms at the 95th percentile, for up to 2,000 open Build Orders."
  3. To the first question you put, if it is about KIT-4's pick lead time:
     "Use the 5 working days the Part Kits page documents."
  After your reply to that first answer, the user sends nothing more: end the
  run with that reply as your last message, and do not take any further
  scripted or plausible answer.
---

/srd:questions initiatives/part-kit-tracking/srd.md
