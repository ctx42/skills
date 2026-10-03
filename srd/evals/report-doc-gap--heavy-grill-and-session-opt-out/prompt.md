---
tags: [case:report-doc-gap--heavy-grill-and-session-opt-out, skill:report-doc-gap, sec:report-doc-gap:usage, sec:report-doc-gap:boundaries, sec:report-doc-gap:support-files, sec:report-doc-gap:invocation, sec:report-doc-gap:workflow, sec:report-doc-gap:the-gap-tools, sec:report-doc-gap:the-gap-record, ref:create/project-config, skill:grill-me]
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
  message you would send the user at that point. That message must appear
  as visible reply text in this run before you continue; never answer
  silently.

  Scripted answers (pick the one that fits the question):
  1. Offered the unreported draft doc gaps: "Work them now."
  2. Asked how deep to go on the first gap (the retry count): "Heavy."
  3. Any interview question about the retry count: "The gateway retries a
     failed upstream call 3 times, 2 seconds apart, then answers 502. Ops
     calls it a resend. That is all I know."
  4. Shown an assembled record and asked whether to file it: "File it."
  5. Asked how deep to go on any later gap: "Just take the one-liners for the
     rest of these."
---

/srd:report-doc-gap specs/gateway.md
