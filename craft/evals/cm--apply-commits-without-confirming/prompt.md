---
tags: [case:cm--apply-commits-without-confirming, skill:cm, needs-shell, sec:cm:usage, sec:cm:input, sec:cm:arguments, sec:cm:workflow, sec:cm:describe-changes-only, sec:cm:structure, sec:cm:summary-line, sec:cm:body-kernel-style, sec:cm:footers, sec:cm:output]
runs: 1
max_turns: 30
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill, Bash(git:*)]
append_system_prompt: |
  The user writes English; reply in English.

  Attribution for git commits you create from here on:
  - End git commit messages with:
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
---

/craft:cm micro apply
