---
tags: [case:review--learn-from-the-session--gate, skill:review, sec:review:usage, sec:review:working-diff-injected, sec:review:rule-edit-and-learn-modes, ref:review/rule-editing]
runs: 1
max_turns: 30
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash(git:*)]
append_system_prompt: |
  The user writes English; reply in English.
  Eval wiring: this workspace is the go plugin's git clone, checked out at
  ./go (the run loads a read-only copy of it). Wherever the skill names
  `../style/SKILL.md` or `../style/rules.md`, use ./go/skills/style/SKILL.md and
  ./go/skills/style/rules.md in this workspace; they are the writable clone.
---

/go:review learn
