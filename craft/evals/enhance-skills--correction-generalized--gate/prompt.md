---
tags: [case:enhance-skills--correction-generalized--gate, skill:enhance-skills, sec:enhance-skills:usage, sec:enhance-skills:lessons-store, sec:enhance-skills:harvest, sec:enhance-skills:lesson-format, sec:enhance-skills:output, sec:enhance-skills:self-learning]
runs: 1
max_turns: 40
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
  Eval wiring: this workspace is the user's writable git checkout of the
  ctx42-skills plugins. The skills this session used ran from it (./go/skills/review/), not
  from the read-only plugin copy this run loads: read and write those workspace
  files, never the loaded copy. The environment sets AGENT_DATA_DIR to
  `.agent-data` at the root of this workspace, so
  `${AGENT_DATA_DIR:-$HOME/.agent-data}` resolves to ./.agent-data here; never
  touch the real home directory.
---

/craft:enhance-skills
