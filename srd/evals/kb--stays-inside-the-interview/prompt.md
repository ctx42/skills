---
tags: [case:kb--stays-inside-the-interview, skill:kb, sec:kb:boundaries, sec:kb:the-kb-folder, sec:kb:invocation, sec:kb:workflow, sec:kb:page-anatomy, sec:kb:open-questions, sec:kb:output, ref:kb/retrieval-authoring, ref:create/project-config, ref:create/doc-corpus]
runs: 1
max_turns: 40
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.
  Before taking a scripted answer, write out in full, as your reply text, the
  message you would send the user at that point.

  Session so far, before the user typed the command: an SRD interview on
  `initiatives/hydrophone-sensor-types/srd.md`.

  You (the agent): ST-3 says a value outside the allowed set is rejected. What
  is the allowed set for the Channel's sensor-type field?

  User: The Asset Service accepts exactly five values on that tag, lowercase:
  `vib`, `hyd`, `pres`, `temp`, `flow`. Anything else is rejected with a
  validation error.

  Nothing in the session mentioned valves, valve maintenance, or any asset
  other than Channels and their sensors. Whether the field may be empty has not
  been asked yet.

  Scripted answers:
  1. To a restatement or confirmation of the allowed sensor-type values: "Yes,
     correct."
  2. To any question about whether the sensor-type field may be empty: "skip
     that for now".
  3. To any question about valves: "Gate valves are serviced every 12 months."
---

/srd:kb capture
