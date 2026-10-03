---
tags: [case:reshape--proposals-stay-on-the-library, skill:reshape, sec:reshape:target, sec:reshape:modifiability, sec:reshape:workflow, sec:reshape:change-archetypes, sec:reshape:impact-rubric, sec:reshape:output, sec:reshape:self-learning, ref:reshape/change-catalog, sec:style:production, sec:reshape:usage]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, LSP, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/go:reshape oskit in ./pkg/render
