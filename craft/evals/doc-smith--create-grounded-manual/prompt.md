---
tags: [case:doc-smith--create-grounded-manual, skill:doc-smith, sec:doc-smith:usage, sec:doc-smith:whole-document-pass-all-modes, sec:doc-smith:self-learning, ref:doc-smith/writing-guide, sec:doc-smith:create-mode]
runs: 1
max_turns: 60
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

  1. Accountants at our customer companies who pay for the service; they are not technical. Key tasks: find and download an invoice, pay an open invoice, update the payment method, and check usage. Call them invoices everywhere, never bills. Write it to docs/user-manual.md.
  2. The outline is fine, go ahead.
---

/craft:doc-smith create a user manual for the billing dashboard
