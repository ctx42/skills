---
tags: [case:system-check--terse-output, skill:system-check, sec:system-check:boundaries, sec:system-check:support-files, sec:system-check:documentation-corpus, sec:system-check:invocation, sec:system-check:review-default, sec:system-check:questions-file, sec:system-check:walk, skill:review, sec:review:boundaries, sec:review:sources-of-truth, sec:review:documentation-corpus, sec:review:severity, sec:review:category, sec:review:modes, sec:review:review-file-format, sec:review:review-default, ref:review/review-file, ref:create/authoring-guide, ref:create/errata, ref:create/srd-procedures, ref:create/project-config, ref:create/doc-corpus]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

/srd:system-check specs/labeling.md
