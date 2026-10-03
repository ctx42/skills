---
tags: [case:create--self-check-catches-violations, skill:create, sec:create:usage, sec:create:boundaries, sec:create:sources-of-truth, sec:create:workflow, ref:create/project-config, ref:create/srd-procedures, ref:create/authoring-guide]
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
  message you would send the user at that point, as visible text and not
  only in thinking.

  Scripted answers (pick the one that fits the question):
  1. Objective: "A Project's admins schedule a recurring CSV export of the
     Project's Sensor readings. Put the SRD at
     initiatives/scheduled-export/srd.md."
  2. UI change: "No."
  3. In Scope: "Two items, word for word. SC-1: Running a recurring export
     at the time an admin schedules. SC-2: Emailing a download link to the
     admins when an export finishes."
  4. Out of Scope: "Exports in any format other than CSV."
  5. Requirements: "Take these three word for word:
     'The system must run each scheduled export at the time the admin set.'
     'The system MUST write each export as a CSV file and MUST delete export
     files older than 7 days.'
     'The system MUST name each export file after the Project and the export
     date. Example: plant-north-2026-10-01.csv'"
  6. Any offer during the interview to reword, split, or restate a
     requirement or scope item differently: "No, keep my wording exactly."
  7. Any further rule: "Nothing else; only what I said."
  8. Any restatement or summary to confirm: "Yes, correct."
  9. A proposed requirement grouping or prefixes: "Fine, use those."
  10. A self-check blocker: "Leave it."
---

/srd:create
