---
tags: [case:create--house-extensions, skill:create, sec:create:usage, sec:create:sources-of-truth, sec:create:workflow, ref:create/project-config, ref:create/srd-procedures, ref:create/authoring-guide]
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
  message you would send the user at that point, as visible text and not
  only in thinking.

  Scripted answers (pick the one that fits the question):
  1. Objective: "Show each Leak Instance's severity as a colored badge in the
     Infobar and keep that severity current. Put the SRD at
     initiatives/leak-severity/srd.md."
  2. UI change: "Yes, the badge in the Infobar."
  3. In Scope: "Two items, word for word. SC-1: Recomputing a Leak
     Instance's severity when new evidence arrives. SC-2: Showing the
     severity as a badge in the Infobar."
  4. Out of Scope: "Changing how the severity score itself is calculated."
  5. Requirements: "Take these word for word:
     'The system MUST recompute a Leak Instance's severity when a measurement
     is added to it.'
     'The severity badge colour MUST standardise on the platform's severity
     palette.'
     'The system MUST show the severity badge in the Infobar of the selected
     Leak Instance.'
     'The Infobar MUST display the severity badge for the Leak Instance that
     is selected.'
     And three badge-label rules that belong together:
     'The badge MUST read High when the severity score is 70 or more.'
     'The badge MUST read Medium when the severity score is from 30 to 69.'
     'The badge MUST read Low when the severity score is below 30.'"
  6. Any offer during the interview to reword, merge, or restate a
     requirement or scope item differently: "No, keep my wording exactly."
  7. Any further rule: "Nothing else; only what I said."
  8. Any restatement or summary to confirm: "Yes, correct."
  9. A proposed requirement grouping or prefixes: "Fine, use those."
  10. A self-check blocker: "Leave it."
---

/srd:create
