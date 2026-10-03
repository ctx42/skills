---
tags: [case:report-doc-gap--opt-out-and-duplicate-merge, skill:report-doc-gap, sec:report-doc-gap:usage, sec:report-doc-gap:boundaries, sec:report-doc-gap:support-files, sec:report-doc-gap:invocation, sec:report-doc-gap:workflow, sec:report-doc-gap:the-gap-tools, sec:report-doc-gap:the-gap-record, ref:create/project-config]
runs: 1
max_turns: 40
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
  1. Shown the assembled record and asked whether to file it: "File it."
  2. Asked how deep to go on a gap: "Skip the questions."
---

/srd:report-doc-gap specs/gateway.md

Hand-over from an srd:system-check pass on specs/gateway.md: no corpus
document states how many times the API Gateway retries a failed upstream
call. kind: missing. demand: GW-2 logs each of the gateway's 3× retries, and
the retry count cannot be confirmed. Searches tried: "API gateway resend
attempts", "retry policy upstream"; no relevant hit.

Once it is captured, work this SRD's drafts with me now. Skip the questions.
