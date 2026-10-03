---
tags: [case:readme-smith--declined-go-source-gate--gate, skill:readme-smith, sec:readme-smith:usage, sec:readme-smith:non-negotiables-both-modes, sec:readme-smith:verify, sec:readme-smith:self-learning, ref:readme-smith/template, sec:readme-smith:improve-mode, sec:readme-smith:go-example-injection-gomake, ref:readme-smith/gomake, needs-shell]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash(go:*), Bash(gomake:*), Bash(make:*), Bash(git:*), Bash(ls:*)]
append_system_prompt: |
  The user writes English; reply in English.
  Automated eval: the user is absent. Only the answers below are scripted.
  Whenever the skill would stop and wait for the user, take the next scripted
  answer below as the reply and continue in this same run. Once the scripted
  answers are used up, at the next point where the skill would wait for the
  user, end the run there: that message is your final reply.

  1. Approved. Apply all the findings.
---

/craft:readme-smith improve pkg/store/README.md
