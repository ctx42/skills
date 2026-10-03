---
tags: [case:create--undocumented-platform-fact, skill:create, skill:report-doc-gap, skill:kb, sec:create:usage, sec:create:sources-of-truth, sec:create:documentation-corpus, sec:create:workflow, ref:create/project-config, ref:create/doc-corpus, ref:create/srd-procedures, ref:create/authoring-guide, sec:report-doc-gap:invocation, sec:report-doc-gap:workflow, sec:report-doc-gap:the-gap-tools, sec:report-doc-gap:the-gap-record, sec:kb:invocation, sec:kb:workflow, sec:kb:the-kb-folder, sec:kb:page-anatomy, sec:kb:boundaries, ref:kb/retrieval-authoring]
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
  1. Objective: "Email a Project's admins when a scheduled data export has
     failed for good."
  2. UI change: "No."
  3. In Scope: "Defer it; derive it from the requirements."
  4. Out of Scope: "Changing how the gateway retries exports."
  5. Requirements: "When an export has failed for good, the system emails
     every admin of the export's Project. The gateway already retries a
     failed export three times, so 'failed for good' means the third retry
     failed too."
  6. Whether three retries is the count today: "Yes, three retries today."
  7. Any further rule (message content, timing, other channels, other
     recipients, anything else): "Nothing else; only what I said."
  8. Any restatement or summary to confirm, including one that proposes an
     SRD path: "Yes, correct."
  9. Where to save the SRD, if asked outright: "Use the path you proposed."
  10. A proposed requirement grouping or prefixes: "Fine, use those."
  11. A self-check blocker: "Leave it."
  12. How deep to go on a documentation gap: "Light."
  13. An offer to file documentation gaps, or an assembled gap record:
      "File it."
---

/srd:create
