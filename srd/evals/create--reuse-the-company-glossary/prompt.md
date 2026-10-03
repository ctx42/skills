---
tags: [case:create--reuse-the-company-glossary, skill:create, sec:create:usage, sec:create:sources-of-truth, sec:create:workflow, ref:create/project-config, ref:create/srd-procedures, ref:create/authoring-guide]
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
  1. Objective: "The system deletes Audit Log entries once their Retention
     Period has passed. Put the SRD at
     initiatives/audit-log-retention/srd.md."
  2. UI change: "No."
  3. In Scope: "Defer it; derive it from the requirements."
  4. Out of Scope: "Exporting the Audit Log, and changing what the Audit Log
     records."
  5. Requirements: "The system deletes each Audit Log entry once its
     Retention Period has elapsed. The Retention Period is 365 days unless a
     Super Admin sets another one for the Project. A Super Admin can set a
     Project's Retention Period from 30 to 3650 days."
  6. Any further rule: "Nothing else; only what I said."
  7. What "Retention Period" means: "How long the system keeps an Audit Log
     entry."
  8. What "Audit Log" means: "It's the Audit Log from the Company Glossary."
  9. What "Super Admin" means: "A user with full administrative rights on the
     INFRAPORT Instance."
  10. Any restatement or summary to confirm: "Yes, correct."
  11. A proposed requirement grouping or prefixes: "Fine, use those."
  12. A self-check blocker: "Leave it."
---

/srd:create
