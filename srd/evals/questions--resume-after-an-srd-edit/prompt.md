---
tags: [case:questions--resume-after-an-srd-edit, skill:questions, sec:questions:boundaries, sec:questions:support-files, sec:questions:documentation-corpus, sec:questions:invocation, sec:questions:review-default, sec:questions:questions-file, sec:questions:walk, sec:questions:re-run-after-an-srd-edit, skill:review, sec:review:boundaries, sec:review:sources-of-truth, sec:review:documentation-corpus, sec:review:severity-and-category, ref:review/finding-tags, sec:review:modes, sec:review:review-file-format, sec:review:review-default, ref:review/review-file, ref:create/authoring-guide, ref:create/errata, ref:create/srd-procedures, sec:review:check, ref:review/check-mode, ref:create/project-config, ref:create/doc-corpus]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/srd:questions initiatives/part-kit-tracking/srd.md
