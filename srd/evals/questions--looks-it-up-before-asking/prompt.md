---
tags: [case:questions--looks-it-up-before-asking, skill:questions, sec:questions:boundaries, sec:questions:support-files, sec:questions:documentation-corpus, sec:questions:invocation, sec:questions:review-default, sec:questions:questions-file, sec:questions:walk, sec:questions:re-run-after-an-srd-edit, sec:questions:platform-knowledge, skill:review, sec:review:boundaries, sec:review:sources-of-truth, sec:review:documentation-corpus, sec:review:severity-and-category, ref:review/finding-tags, sec:review:modes, sec:review:review-file-format, sec:review:review-default, ref:review/review-file, ref:create/authoring-guide, ref:create/errata, ref:create/srd-procedures, skill:kb, sec:kb:boundaries, sec:kb:the-kb-folder, sec:kb:the-corpus, sec:kb:invocation, sec:kb:workflow, ref:kb/page-anatomy, sec:kb:output, ref:kb/retrieval-authoring, ref:kb/conflicts, ref:create/project-config, ref:create/doc-corpus]
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
  2. To the first question you put: if it is about the pick priority of a new
     Part Kit: "For this SRD, new Part Kits get the pick priority `routine`.
     And remember that kits can't span bays." To any other first question:
     "Leave it as written for now. And remember that kits can't span bays."
  3. To any question about what that means: "A Part Kit is staged in one
     Assembly Bay only; it is never split across bays."
  4. To your restatement or any confirmation: "Yes, correct."
  5. After that: "Stop here for now."
---

/srd:questions initiatives/part-kit-tracking/srd.md
