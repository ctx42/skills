---
tags: [case:kb--writes-only-what-was-attested, skill:kb, sec:kb:boundaries, sec:kb:the-kb-folder, sec:kb:invocation, sec:kb:workflow, sec:kb:page-anatomy, sec:kb:open-questions, sec:kb:output, ref:kb/retrieval-authoring, ref:create/project-config, ref:create/doc-corpus]
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

  Session so far, before the user typed the command (no SRD is in play):

  User: How do leak instances work again? I want to get this straight. A leak
  instance accumulates evidence. It starts from the AUTOCO detection somebody
  set to To check, and then every measurement a technician adds from the field
  gets attached to that same leak instance. Nothing replaces earlier evidence:
  adding a measurement never removes or overwrites one that's already there.

  You (the agent): Understood. Evidence that piles up like that is presumably
  retained for 12 months and then purged.

  (The user never answered or confirmed that last remark.)

  Scripted answers:
  1. To a restatement or confirmation of how Leak Instances accumulate
     evidence: "Yes, that's right."
  2. To any question about how long evidence is kept, or whether it expires:
     "No idea, skip it."
---

/srd:kb capture
