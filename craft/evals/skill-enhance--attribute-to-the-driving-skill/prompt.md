---
tags: [case:skill-enhance--attribute-to-the-driving-skill, skill:skill-enhance, sec:skill-enhance:usage, sec:skill-enhance:lessons-store, sec:skill-enhance:harvest, sec:skill-enhance:lesson-format, sec:skill-enhance:output, sec:skill-enhance:self-learning]
runs: 1
max_turns: 40
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
  Eval wiring: this workspace is the user's writable git checkout of the
  ctx42-skills plugins. The skills this session used ran from it (./craft/skills/cm/, ./srd/skills/create/), not
  from the read-only plugin copy this run loads: read and write those workspace
  files, never the loaded copy. The environment sets AGENT_DATA_DIR to
  `.agent-data` at the root of this workspace, so `$AGENT_DATA_DIR` replaces
  `~/.agent-data` and the lessons store is ./.agent-data here; never touch the
  real home directory.
  srd:create loads the SRD standard live from the srd server, which this
  run does not have; the frozen copy at
  ./srd/evals/mocks/srd/fixtures/srd-standard.md is identical to it.

  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.
  Before taking a scripted answer, write out in full, as your reply text, the
  message you would send the user at that point.

  1. Yes, write it.
---

/craft:skill-enhance
