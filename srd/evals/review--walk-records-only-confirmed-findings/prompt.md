---
tags: [case:review--walk-records-only-confirmed-findings, skill:review, sec:review:boundaries, sec:review:sources-of-truth, sec:review:modes, ref:create/project-config, sec:review:severity, sec:review:category, sec:review:review-file-format, ref:review/review-file, sec:review:usage, sec:review:documentation-corpus, ref:create/authoring-guide, ref:create/doc-corpus, ref:create/errata, ref:create/srd-procedures, sec:review:walk]
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
  message you would send the user at that point.

  Scripted answers (pick the one that fits the question):
  1. Metadata findings: "Keep them all."
  2. Introduction findings: "Reject them: they are invalid. Record nothing for
     the Introduction."
  3. Glossary or Scope findings: "Keep them all."
  4. Requirements findings: "Keep them all except the British-spelling finding
     about `behaviour`: that one is invalid, drop it."
  5. Any other section's findings: "Keep them all."
  6. An offer to work documentation gaps: "No, leave them."
---

/srd:review specs/login.md walk
