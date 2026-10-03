---
tags: [case:report-doc-gap--drain-grill-confirm-file, skill:report-doc-gap, sec:report-doc-gap:usage, sec:report-doc-gap:boundaries, sec:report-doc-gap:support-files, sec:report-doc-gap:invocation, sec:report-doc-gap:workflow, sec:report-doc-gap:the-gap-tools, sec:report-doc-gap:the-gap-record, ref:create/project-config]
runs: 1
max_turns: 50
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.
  Before taking a scripted answer, write out in full, as your reply text, the
  message you would send the user at that point. That message must appear
  as visible reply text in this run before you continue; never answer
  silently.

  Scripted answers (pick the one that fits the question):
  1. Offered the unreported draft doc gaps: "Work them now."
  2. Asked how deep to go on a gap: "Light."
  3. Asked to confirm or sharpen a gap's one-line detail: "It's fine as it is."
  4. Shown an assembled record and asked whether to file it: "Yes, file it."
---

/srd:report-doc-gap specs/gateway.md
