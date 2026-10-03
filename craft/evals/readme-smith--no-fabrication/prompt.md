---
tags: [case:readme-smith--no-fabrication, skill:readme-smith, sec:readme-smith:usage, sec:readme-smith:non-negotiables-both-modes, sec:readme-smith:verify, sec:readme-smith:self-learning, ref:readme-smith/template, sec:readme-smith:create-mode, needs-shell]
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

  1. Positioning: portcheck is for SREs and on-call engineers who must
     confirm, before a deploy, that every host:port a service depends on
     accepts connections. Lead with concurrent dials, the per-target
     timeout, and JSON output for scripts. No roadmap to mention.
  2. To any other question (versions, releases, licensing, platforms,
     performance): "I don't know."
---

/craft:readme-smith create a README
