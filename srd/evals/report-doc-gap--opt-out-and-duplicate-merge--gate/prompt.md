---
tags: [case:report-doc-gap--opt-out-and-duplicate-merge--gate, skill:report-doc-gap, sec:report-doc-gap:usage, sec:report-doc-gap:boundaries, sec:report-doc-gap:support-files, sec:report-doc-gap:invocation, sec:report-doc-gap:workflow, sec:report-doc-gap:the-gap-tools, sec:report-doc-gap:the-gap-record, ref:create/project-config]
runs: 1
max_turns: 30
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

/srd:report-doc-gap specs/gateway.md

Hand-over from an srd:system-check pass on specs/gateway.md: no corpus
document states how many times the API Gateway retries a failed upstream
call. kind: missing. demand: GW-2 logs each of the gateway's 3× retries, and
the retry count cannot be confirmed. Searches tried: "API gateway resend
attempts", "retry policy upstream"; no relevant hit.

Once it is captured, work this SRD's drafts with me now. Skip the questions.
