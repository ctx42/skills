---
tags: [case:system-check--stale-citation-becomes-a-question, skill:system-check, sec:system-check:boundaries, sec:system-check:support-files, sec:system-check:documentation-corpus, sec:system-check:invocation, sec:system-check:review-default, sec:system-check:questions-file, sec:system-check:walk, sec:system-check:platform-knowledge, skill:review, sec:review:boundaries, sec:review:sources-of-truth, sec:review:documentation-corpus, sec:review:severity, sec:review:category, sec:review:modes, sec:review:review-file-format, sec:review:review-default, ref:review/review-file, ref:create/authoring-guide, ref:create/errata, ref:create/srd-procedures, skill:kb, sec:kb:boundaries, sec:kb:the-kb-folder, sec:kb:the-corpus, sec:kb:invocation, sec:kb:workflow, sec:kb:page-anatomy, sec:kb:output, ref:kb/retrieval-authoring, skill:report-doc-gap, sec:report-doc-gap:boundaries, sec:report-doc-gap:invocation, sec:report-doc-gap:workflow, ref:create/project-config, ref:create/doc-corpus]
runs: 1
max_turns: 80
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.
  Before taking a scripted answer, write out in full, as your reply text, the
  message you would send the user at that point.

  Scripted answers (pick the one that fits):
  1. To any offer about documentation gaps, drafts, or filing: "Keep them as
     drafts for later; no time to grill them today."
  2. To a question about GR-7's lookup speed: "300 ms at the 95th percentile,
     for a Project holding up to 500,000 Sound Files."
  3. To a question about whether the platform still imports `meta` tags as
     Tags, or about the vanished document: "Yes, that still holds: every meta
     tag comes in as a Tag under `snd`, same name. The page it pointed at was
     deleted in a Confluence clean-up."
  4. To your restatement or any confirmation: "Yes, correct."
  5. After each answered question: "next"
  6. To any other question: "Leave it as written; next."
---

/srd:system-check specs/labeling.md
