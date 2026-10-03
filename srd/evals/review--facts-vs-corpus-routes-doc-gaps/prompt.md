---
tags: [case:review--facts-vs-corpus-routes-doc-gaps, skill:review, sec:review:boundaries, sec:review:sources-of-truth, sec:review:modes, ref:create/project-config, sec:review:severity, sec:review:category, sec:review:review-file-format, ref:review/review-file, sec:review:usage, sec:review:documentation-corpus, sec:review:review-default, ref:create/authoring-guide, ref:create/doc-corpus, ref:create/errata, ref:create/srd-procedures, skill:report-doc-gap, sec:report-doc-gap:boundaries, sec:report-doc-gap:invocation, sec:report-doc-gap:workflow, sec:report-doc-gap:the-gap-tools, sec:report-doc-gap:the-gap-record, sec:report-doc-gap:the-doc-gap-vs-srd-gap-boundary]
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
  message you would send the user at that point.

  Scripted answers (pick the one that fits the question):
  1. Offered the unreported draft doc gaps a prior session left for this SRD:
     "Keep them as drafts for later."
  2. Offered to work the doc gaps this review captured: "Later, not now."
  3. Any other question: "Leave it as it is."
---

/srd:review specs/gateway.md
