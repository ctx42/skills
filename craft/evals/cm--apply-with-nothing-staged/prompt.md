---
tags: [case:cm--apply-with-nothing-staged, skill:cm, needs-shell, sec:cm:usage, sec:cm:input, sec:cm:arguments, sec:cm:workflow, sec:cm:describe-changes-only, sec:cm:structure, sec:cm:summary-line, sec:cm:body-kernel-style, sec:cm:footers, sec:cm:output]
runs: 1
max_turns: 30
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill, Bash(git:*)]
append_system_prompt: |
  The user writes English; reply in English.
---

/craft:cm apply
