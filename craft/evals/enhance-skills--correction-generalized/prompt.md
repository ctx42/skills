---
tags: [case:enhance-skills--correction-generalized, skill:enhance-skills, sec:enhance-skills:usage, sec:enhance-skills:lessons-store, sec:enhance-skills:harvest, sec:enhance-skills:lesson-format, sec:enhance-skills:output, sec:enhance-skills:self-learning]
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

  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.
  Before taking a scripted answer, write out in full, as your reply text, the
  message you would send the user at that point.

  1. Yes, write it.
---

/craft:enhance-skills
