---
tags: [case:system-check--learn-banks-only-uncovered-facts--gate, skill:system-check, sec:system-check:boundaries, sec:system-check:invocation, sec:system-check:learn, sec:system-check:platform-knowledge, skill:kb, sec:kb:boundaries, sec:kb:the-kb-folder, sec:kb:the-corpus, sec:kb:invocation, sec:kb:workflow, sec:kb:page-anatomy, sec:kb:output, ref:kb/retrieval-authoring, ref:create/project-config, ref:create/doc-corpus]
runs: 1
max_turns: 40
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
  Session so far, before the user typed the command: a debugging session on
  failed Sound File imports. `specs/labeling.md` is open in the editor and was
  mentioned once, but the session is not SRD work.

  User: The import job keeps failing for the Zurich batch. Can you look at the
  log?

  You (the agent): Two kinds of errors: `413 payload too large` on six WAV
  files, and `invalid tag name "2fa_score"` on one metadata write.

  User: Right, the 413s are the size cap: the platform rejects any Sound File
  upload larger than 20 MB. Those Zurich files are long hydrophone recordings.

  You (the agent): And the tag error?

  User: Tag node names have to start with a letter a-z, so "2fa_score" is
  invalid. Rename it "score_2fa".

  You (the agent): Understood. (Aside: the importer probably retries the 413s
  before giving up, which would explain the long run time.)

  User: Maybe, not sure. Anyway, our labeling SRD says Tag lookups must come
  back within 300 ms; keep that in mind for the importer too.

  You (the agent): Noted. I'll split the six files and rename the tag.
---

/srd:system-check learn
