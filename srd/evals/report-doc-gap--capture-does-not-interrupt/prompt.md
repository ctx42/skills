---
tags: [case:report-doc-gap--capture-does-not-interrupt, skill:report-doc-gap, sec:report-doc-gap:usage, sec:report-doc-gap:boundaries, sec:report-doc-gap:support-files, sec:report-doc-gap:invocation, sec:report-doc-gap:workflow, sec:report-doc-gap:the-gap-tools, sec:report-doc-gap:the-gap-record, ref:create/project-config, skill:review, sec:review:usage, sec:review:boundaries, sec:review:sources-of-truth, sec:review:documentation-corpus, sec:review:modes, sec:review:review-file-format, sec:review:review-default, ref:review/review-file, ref:create/doc-corpus, ref:create/authoring-guide, ref:create/errata, ref:create/srd-procedures, sec:report-doc-gap:the-doc-gap-vs-srd-gap-boundary]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

/srd:review specs/gateway.md
