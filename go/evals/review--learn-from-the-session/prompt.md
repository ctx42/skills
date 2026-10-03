---
tags: [case:review--learn-from-the-session, skill:review, sec:review:usage, sec:review:working-diff-injected, sec:review:rule-edit-and-learn-modes, ref:review/rule-editing]
runs: 1
max_turns: 40
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash(git:*)]
append_system_prompt: |
  The user writes English; reply in English.
  Eval wiring: this workspace is the go plugin's git clone, checked out at
  ./go (the run loads a read-only copy of it). Wherever the skill names
  `../style/SKILL.md` or `../style/rules.md`, use ./go/skills/style/SKILL.md and
  ./go/skills/style/rules.md in this workspace; they are the writable clone.

  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.
  Before taking a scripted answer, write out in full, as your reply text, the
  message you would send the user at that point.

  1. Keep both new rules.
---

/go:review learn
