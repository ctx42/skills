---
tags: [case:readme-smith--terse-output, skill:readme-smith, sec:readme-smith:usage, sec:readme-smith:non-negotiables-both-modes, sec:readme-smith:verify, sec:readme-smith:self-learning, ref:readme-smith/template, sec:readme-smith:improve-mode, needs-shell]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash(go:*), Bash(gomake:*), Bash(make:*), Bash(git:*), Bash(ls:*)]
append_system_prompt: |
  The user writes English; reply in English.
  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.
  Before taking a scripted answer, write out in full, as your reply text, the
  message you would send the user at that point.

  1. Approved. Apply all the findings.
  2. To any other question: "No, leave it."
---

/craft:readme-smith improve README.md
