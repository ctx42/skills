---
tags: [case:kb--writes-to-the-inbox-at-confirmation, skill:kb, skill:create, sec:kb:boundaries, sec:kb:the-kb-folder, sec:kb:invocation, sec:kb:workflow, ref:kb/page-anatomy, sec:kb:output, ref:kb/retrieval-authoring, sec:create:documentation-corpus, sec:create:workflow, ref:create/project-config, ref:create/doc-corpus, ref:create/srd-procedures, ref:create/authoring-guide]
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
  message you would send the user at that point.

  Scripted answers (pick the one that fits the question):
  1. Summary or purpose: "Let a customer swap a mission's launch slot for
     another free slot through the Booking API. Put the SRD at
     initiatives/slot-swap/srd.md."
  2. Whether it changes what users see: "No."
  3. Included items: "Defer it; derive them from the requirements."
  4. Excluded items: "Swaps through the Mission Dashboard, changes to the slot
     fee, and swaps into another launch window."
  5. Requirements: "A customer may swap a mission's launch slot for another
     free slot in the same launch window, until 14 days before launch and at
     most once per mission. The Booking API already identifies each slot
     booking by its booking reference, sent in the X-Booking-Ref request
     header, and each customer mission has exactly one active slot booking.
     A refused swap is answered with HTTP 409 and the reason in the response
     body. Customer success can raise a mission's swap allowance, from 1 to 3
     swaps."
  6. Requests with no booking reference or an unknown one: "Not in this SRD."
  7. Any restatement or summary to confirm: "Yes, correct."
  8. A proposed requirement grouping or prefixes: "Fine, use those."
  9. A self-check blocker: "Leave it."
  10. An offer to file documentation gaps: "File it."
---

/srd:create
