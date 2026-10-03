---
tags: [case:readme-smith--gomake-installed-but-project-does-not-use-it, skill:readme-smith, sec:readme-smith:usage, sec:readme-smith:non-negotiables-both-modes, sec:readme-smith:verify, sec:readme-smith:self-learning, ref:readme-smith/template, sec:readme-smith:create-mode, sec:readme-smith:go-example-injection-gomake, ref:readme-smith/gomake, needs-shell]
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

  1. Positioning: linecount is for developers who want a quick count of
     non-blank lines per file without wc's blank-line noise. Lead with the
     -all flag. No roadmap.
  2. To any other question: "I don't know."
---

/craft:readme-smith write a README
