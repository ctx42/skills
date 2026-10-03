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
  1. Objective, or a restatement of it: "Yes: a user who forgot their
     password resets it themselves through a link emailed to their account
     address. Put the SRD at initiatives/password-reset/srd.md."
  2. UI change: "Yes: a 'Forgot password?' link on the Log In Page and a page
     where the user sets the new password."
  3. In Scope: "Defer it; derive it from the requirements."
  4. Out of Scope: "Resets by SMS, and resets an administrator starts for a
     user."
  5. Requirements: "When a user requests a reset, the system emails a reset
     link to the account's address and signs the user out of every other
     session. Resets must be secure."
  6. What "secure" means, or a measurable form for it: "A reset link expires
     30 minutes after it is sent."
  7. Any further rule (unknown addresses, rate limits, password rules, link
     reuse, anything else): "Nothing else; only what I said."
  8. A term to define: "Reset Link: the link emailed to a user that opens the
     page where they set a new password."
  9. Any restatement or summary to confirm: "Yes, correct."
  10. A proposed requirement grouping or prefixes: "Fine, use those."
  11. A self-check blocker: "Leave it."
---

/srd:create — we need an SRD for a password reset feature
