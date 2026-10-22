---
tags: [case:fold-lessons--gate-lessons-and-edits, skill:fold-lessons, needs-shell, sec:fold-lessons:usage, sec:fold-lessons:generic-or-not, sec:fold-lessons:validate, sec:fold-lessons:procedure, sec:fold-lessons:output, sec:fold-lessons:self-learning]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash(git:*), Bash(./dev/lint-skills.sh:*), Bash(./dev/eval-routine.sh:*), Bash(./dev/eval-probe.py:*)]
append_system_prompt: |
  The user writes English; reply in English.
  Eval wiring: this workspace is the user's writable git checkout of the
  ctx42-skills plugins; the skills to fold live here, not in the read-only
  plugin copy this run loads. The environment sets AGENT_DATA_DIR to
  `.agent-data` at the root of this workspace, so `$AGENT_DATA_DIR` replaces
  `~/.agent-data` here; never touch the real home directory.
---

/craft:fold-lessons
