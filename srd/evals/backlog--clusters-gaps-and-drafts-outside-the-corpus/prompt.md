---
tags: [case:backlog--clusters-gaps-and-drafts-outside-the-corpus, skill:backlog, sec:backlog:usage, sec:backlog:boundaries, sec:backlog:sources-of-truth, sec:backlog:backends, sec:backlog:workflow, ref:create/project-config, ref:create/doc-corpus, ref:kb/retrieval-authoring]
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

  1. To which cluster to work: "The Sound File retention one."
  2. To any question about the fact the page must state: "Raw Sound Files are deleted 400 days after upload, archived or not. Only an EXAMPLE administrator can change that period, and only for a whole EXAMPLE Instance. The 90-day move to the archive tier stays as documented."
  3. To where the draft goes: "Put it at `drafts/sound-file-retention.md`."
  4. Once the draft is ready: "I've published it: https://confluence.example.com/example/operations/storage-housekeeping"
  5. To any offer of another cluster or list: "No, that's all for today."
---

/srd:backlog gaps
