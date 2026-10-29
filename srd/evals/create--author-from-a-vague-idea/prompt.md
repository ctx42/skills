---
tags: [case:create--author-from-a-vague-idea, skill:create, sec:create:usage, sec:create:sources-of-truth, sec:create:workflow, ref:create/project-config, ref:create/srd-procedures, ref:create/authoring-guide]
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
  1. Purpose or summary, or a restatement of it: "Yes: a customer moves
     their customer mission to another free launch slot themselves, from the
     Mission Dashboard. Put the SRD at initiatives/slot-swap/srd.md."
  2. UI change: "Yes: a 'Swap slot' button on the Mission Dashboard that
     opens the Slot Picker."
  3. What the SRD delivers (in scope): "Defer it; derive it from the
     requirements."
  4. What it excludes (out of scope): "Swaps that Starforge operations start
     for a customer, and moving a mission to another vehicle."
  5. Requirements: "When a customer confirms a swap, the system releases the
     old launch slot and emails the customer an updated mission manifest.
     Swaps must be timely."
  6. What "timely" means, or a measurable form for it: "A swap is allowed
     until 14 days before the booked launch slot."
  7. Any further rule (swap limits, fees, payload checks, slot holds,
     anything else): "Nothing else; only what I said."
  8. A term to define: "Slot Swap: moving a customer mission from its booked
     launch slot to another free launch slot."
  9. Any restatement or summary to confirm: "Yes, correct."
  10. A proposed requirement grouping or group codes: "Fine, use those."
  11. A self-check blocker: "Leave it."
---

/srd:create — we need an SRD for letting customers swap their launch slot
