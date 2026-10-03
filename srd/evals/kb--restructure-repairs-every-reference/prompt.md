---
tags: [case:kb--restructure-repairs-every-reference, skill:kb, sec:kb:boundaries, sec:kb:the-kb-folder, sec:kb:invocation, sec:kb:page-anatomy, sec:kb:open-questions, sec:kb:restructure, sec:kb:output, ref:kb/restructure, ref:kb/retrieval-authoring, ref:create/project-config, ref:create/doc-corpus]
runs: 1
max_turns: 50
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.
  Before taking a scripted answer, write out in full, as your reply text, the
  message you would send the user at that point.

  Session so far, before the user typed the command:

  User: The gateway firmware fact in the inbox has its own subject, LoRa
  Gateway firmware. Pull it out of the inbox onto a page of its own,
  `kb/lora-gateway-firmware.md`.

  Scripted answers:
  1. To the proposed moves: "Yes, go ahead."
---

/srd:kb restructure
