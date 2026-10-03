---
tags: [case:doc-smith--terse-output, skill:doc-smith, sec:doc-smith:usage, sec:doc-smith:whole-document-pass-all-modes, sec:doc-smith:self-learning, ref:doc-smith/writing-guide, sec:doc-smith:audit-mode, sec:doc-smith:technical-claims-flag-don-t-fix]
runs: 1
max_turns: 40
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.
  Before taking a scripted answer, write out in full, as your reply text, the
  message you would send the user at that point.

  1. Apply all of them.
---

/craft:doc-smith audit docs/manual.md
