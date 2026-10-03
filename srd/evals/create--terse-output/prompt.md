---
tags: [case:create--terse-output, skill:create, sec:create:usage, sec:create:sources-of-truth, sec:create:workflow, ref:create/project-config, ref:create/srd-procedures, ref:create/authoring-guide]
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
  1. Objective: "Email a Project's admins when a Device's battery runs low.
     Put the SRD at initiatives/device-battery-alerts/srd.md."
  2. UI change: "No."
  3. In Scope: "Two items, word for word. SC-1: Emailing admins when a
     Device's battery is low. SC-2: Keeping a log of every low-battery email
     sent."
  4. Out of Scope: "Scheduling battery replacements."
  5. Requirements: "The system emails every admin of the Device's Project
     when the Device reports a battery level below 15 percent. The system
     sends at most one low-battery email per Device per 24 hours."
  6. Any further rule: "Nothing else; only what I said."
  7. Any restatement or summary to confirm: "Yes, correct."
  8. A proposed requirement grouping or prefixes: "Fine, use those."
  9. A self-check blocker (for example a scope item no requirement covers):
     "Leave it."
---

/srd:create
