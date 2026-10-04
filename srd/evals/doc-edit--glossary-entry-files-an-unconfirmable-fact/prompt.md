---
tags: [case:doc-edit--glossary-entry-files-an-unconfirmable-fact, skill:doc-edit, sec:doc-edit:usage, sec:doc-edit:boundaries, sec:doc-edit:sources-of-truth, sec:doc-edit:session-start, sec:doc-edit:edit-loop, sec:doc-edit:facts, sec:doc-edit:document-kinds, sec:doc-edit:session-end, ref:create/project-config, ref:create/doc-corpus, skill:report-doc-gap, sec:report-doc-gap:invocation, sec:report-doc-gap:workflow, sec:report-doc-gap:the-gap-tools, sec:report-doc-gap:the-gap-record]
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

  Scripted answers (pick the one that fits the question):
  1. Asked whether the 02:00–04:00 recording window is right, or to confirm it: "I can't confirm that window — the acoustics team would know. Leave it as it is."
  2. To a proposal adding the same-water-main fact to the Correlation entry: "Y".
  3. To an offer to file, change, or drop a documentation gap: "File it."
  4. Anything else: "That's all — close the session."
---

/srd:doc-edit docs/glossary/main_glossary.md add to the Correlation entry that a correlation run needs two Loggers on the same water main
