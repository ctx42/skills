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
  1. Objective, or a restatement of it: "Yes: the export API limits how many
     export requests each Project may start. Put the SRD at
     initiatives/export-rate-limit/srd.md."
  2. UI change: "No."
  3. In Scope: "Defer it; derive it from the requirements."
  4. Out of Scope: "Limits on any API other than the export API."
  5. Requirements: "The export API accepts at most 10 export requests per
     Project per hour. Over the limit, it rejects the request with HTTP 429."
  6. Any further rule: "Nothing else; only what I said."
  7. Any restatement or summary to confirm: "Yes, correct."
  8. A proposed requirement grouping or prefixes: "Fine, use those."
  9. A self-check blocker: "Leave it."
---

/srd:create a rate limit for the export API
