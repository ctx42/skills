---
tags: [case:create--no-ui-change-sets-designs-na, skill:create, sec:create:usage, sec:create:sources-of-truth, sec:create:workflow, ref:create/project-config, ref:create/srd-procedures, ref:create/authoring-guide]
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
  1. Objective: "The system compresses stored Sound Files once they are 90
     days old, to cut storage cost. Put the SRD at
     initiatives/sound-file-compression/srd.md."
  2. UI change: "No. It's backend-only; nothing in the UI changes."
  3. In Scope: "Defer it; derive it from the requirements."
  4. Out of Scope: "Sound Files younger than 90 days, and deleting Sound
     Files."
  5. Requirements: "The system compresses each stored Sound File with FLAC
     once it is 90 days old. The system deletes the original WAV file only
     after the FLAC copy decodes to the same samples."
  6. Any further rule: "Nothing else; only what I said."
  7. Any restatement or summary to confirm: "Yes, correct."
  8. A proposed requirement grouping or prefixes: "Fine, use those."
  9. A self-check blocker: "Leave it."
---

/srd:create
