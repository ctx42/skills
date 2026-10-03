---
tags: [case:system-check--looks-it-up-before-asking, skill:system-check, sec:system-check:boundaries, sec:system-check:support-files, sec:system-check:documentation-corpus, sec:system-check:invocation, sec:system-check:review-default, sec:system-check:questions-file, sec:system-check:walk, sec:system-check:re-run-after-an-srd-edit, sec:system-check:platform-knowledge, skill:review, sec:review:boundaries, sec:review:sources-of-truth, sec:review:documentation-corpus, sec:review:severity, sec:review:category, sec:review:modes, sec:review:review-file-format, sec:review:review-default, ref:review/review-file, ref:create/authoring-guide, ref:create/errata, ref:create/srd-procedures, skill:kb, sec:kb:boundaries, sec:kb:the-kb-folder, sec:kb:the-corpus, sec:kb:invocation, sec:kb:workflow, sec:kb:page-anatomy, sec:kb:output, ref:kb/retrieval-authoring, ref:create/project-config, ref:create/doc-corpus]
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
  2. To the first question you put: if it is about the Tag Kind of a Label
     Tag: "For this SRD, Label Tags use the Tag Kind `string`. And remember that
     sessions can't span tenants." To any other first question: "Leave it as
     written for now. And remember that sessions can't span tenants."
  3. To any question about what "tenant" means: "A Customer: a user session
     always stays within one Customer."
  4. To your restatement or any confirmation: "Yes, correct."
  5. After that: "Stop here for now."
---

/srd:system-check specs/labeling.md
