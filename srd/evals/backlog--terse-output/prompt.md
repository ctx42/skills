---
tags: [case:backlog--terse-output, skill:backlog, sec:backlog:usage, sec:backlog:boundaries, sec:backlog:sources-of-truth, sec:backlog:backends, sec:backlog:workflow, ref:create/project-config, sec:kb:boundaries, sec:kb:the-kb-folder, sec:kb:invocation, sec:kb:workflow, sec:kb:page-anatomy, sec:kb:open-questions, sec:kb:output, ref:create/doc-corpus, ref:kb/retrieval-authoring]
runs: 1
max_turns: 80
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

  1. To the opening counts: "Start with deferred."
  2. To the battery-low threshold question: "3.4 V."
  3. To the upload interval question: "Every 6 hours."
  4. To the offer of the next list: "Yes, gaps."
  5. To which cluster to work: "That one."
  6. To any question about the gap's fact: "The target claim is right: raw Sound Files are deleted 400 days after upload, archived or not. Nothing to add."
  7. To where the draft goes: "Put it at `drafts/sound-file-retention.md`."
  8. Once the draft is ready: "Published: https://docs.example.com/operations/sound-file-retention"
  9. To anything else: "That's all for today."
---

/srd:backlog
