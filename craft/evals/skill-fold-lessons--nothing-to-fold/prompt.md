---
tags: [case:skill-fold-lessons--nothing-to-fold, skill:skill-fold-lessons, needs-shell, sec:skill-fold-lessons:usage, sec:skill-fold-lessons:generic-or-not, sec:skill-fold-lessons:validate, sec:skill-fold-lessons:procedure, sec:skill-fold-lessons:output, sec:skill-fold-lessons:self-learning]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash(git:*)]
append_system_prompt: |
  The user writes English; reply in English.
  Eval wiring: this workspace is the user's writable git checkout of the
  ctx42-skills plugins; the skills to fold live here, not in the read-only
  plugin copy this run loads. The environment sets AGENT_DATA_DIR to
  `.agent-data` at the root of this workspace, so `$AGENT_DATA_DIR` replaces
  `~/.agent-data` here; never touch the real home directory.
---

/craft:skill-fold-lessons
