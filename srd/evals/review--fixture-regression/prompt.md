---
tags: [case:review--fixture-regression, skill:review, sec:review:boundaries, sec:review:sources-of-truth, sec:review:modes, ref:create/project-config, sec:review:severity, sec:review:category, sec:review:review-file-format, ref:review/review-file, sec:review:usage, sec:review:documentation-corpus, sec:review:review-default, ref:create/authoring-guide, ref:create/doc-corpus, ref:create/errata, ref:create/srd-procedures]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

/srd:review assets/flawed-srd.md
