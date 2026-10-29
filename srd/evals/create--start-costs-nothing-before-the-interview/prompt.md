---
tags: [case:create--start-costs-nothing-before-the-interview, skill:create, sec:create:usage, sec:create:sources-of-truth, sec:create:documentation-corpus, sec:create:workflow, ref:create/project-config, ref:create/doc-corpus, ref:create/srd-procedures, ref:create/authoring-guide]
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
  1. Purpose or summary, or a restatement of it: "Yes: the Build-Time
     Forecast retrains itself every week on recent build orders. Put the SRD
     at initiatives/build-forecast/srd.md."
  2. UI change: "No."
  3. What the SRD delivers (in scope): "Defer it; derive it from the
     requirements."
  4. What it excludes (out of scope): "Changes to the Slot Recommender or the
     Shortage Risk Score."
  5. Requirements: "The system retrains the Build-Time Forecast once a week
     on the build orders finished in the last 180 days. When a retraining run
     fails, the system keeps serving the previous forecast."
  6. Any further rule: "Nothing else; only what I said."
  7. Any restatement or summary to confirm: "Yes, correct."
  8. A proposed requirement grouping or group codes: "Fine, use those."
  9. A self-check blocker: "Leave it."
---

/srd:create weekly retraining for the Build-Time Forecast
