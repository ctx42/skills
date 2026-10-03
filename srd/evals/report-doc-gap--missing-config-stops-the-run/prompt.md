---
tags: [case:report-doc-gap--missing-config-stops-the-run, skill:report-doc-gap, sec:report-doc-gap:usage, sec:report-doc-gap:boundaries, sec:report-doc-gap:support-files, sec:report-doc-gap:invocation, sec:report-doc-gap:workflow, sec:report-doc-gap:the-gap-tools, sec:report-doc-gap:the-gap-record, ref:create/project-config]
runs: 1
max_turns: 20
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

/srd:report-doc-gap specs/gateway.md
