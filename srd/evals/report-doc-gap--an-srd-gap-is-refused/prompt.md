---
tags: [case:report-doc-gap--an-srd-gap-is-refused, skill:report-doc-gap, sec:report-doc-gap:usage, sec:report-doc-gap:boundaries, sec:report-doc-gap:support-files, sec:report-doc-gap:invocation, sec:report-doc-gap:workflow, sec:report-doc-gap:the-gap-tools, sec:report-doc-gap:the-gap-record, ref:create/project-config, sec:report-doc-gap:the-doc-gap-vs-srd-gap-boundary, ref:create/doc-corpus]
runs: 1
max_turns: 30
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

/srd:report-doc-gap specs/gateway.md

Hand-over from an srd:review pass on specs/gateway.md; capture these:

1. The Retention Sweep section (RS-1) cites a 90-day retention window the
   platform docs never state. Searches tried: "retention sweep window",
   "gateway log retention days"; no hit.
2. GR-7 and GR-9 both specify the login lockout threshold and disagree
   (5 failed attempts versus 3).
