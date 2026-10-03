---
tags: [case:kb--bare-capture-with-no-srd, skill:kb, sec:kb:boundaries, sec:kb:the-kb-folder, sec:kb:invocation, sec:kb:workflow, sec:kb:page-anatomy, sec:kb:output, ref:kb/retrieval-authoring, ref:create/project-config, ref:create/doc-corpus]
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

  Session so far, before the user typed the command: a general conversation
  about FTP ingestion. No SRD was opened; no SRD path or id was mentioned.

  User: Why do some files linger on the device FTP folders?

  You (the agent): The docs don't say when ingestion removes files. Do you
  know?

  User: Yes. The FTP ingestion service deletes a file from the device's FTP
  folder only after it has imported that file successfully. A file that fails
  to import stays in the folder and is picked up again on the next polling
  cycle.

  You (the agent): So a file stays until it imports successfully, and failures
  are retried each polling cycle, right?

  User: Correct.

  Scripted answers:
  1. To any further confirmation of that fact: "Yes, correct."
  2. To any question about the polling interval or a retry limit: "Don't know,
     skip it."
---

/srd:kb
