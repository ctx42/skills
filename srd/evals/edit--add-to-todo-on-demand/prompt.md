---
tags: [case:edit--add-to-todo-on-demand, skill:edit, sec:edit:usage, sec:edit:boundaries, sec:edit:sources-of-truth, sec:edit:session-start-every-mode, sec:edit:edit-discipline, sec:edit:modes, sec:edit:session-end-every-mode, sec:edit:self-learning, ref:create/project-config, ref:create/doc-corpus, ref:create/authoring-guide, sec:edit:decision-log, ref:edit/decision-log, sec:edit:draft-scaffolds, ref:edit/draft-scaffolds]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  Session so far: the user ran `/srd:edit specs/login.md`. The srd:edit skill
  front-loaded its issue summary and the user skipped (`S`) its one proposal,
  on GR-2. The edit session on specs/login.md is still running: load the
  srd:edit skill with the Skill tool and continue it with the user's next
  message, which follows.
---

Add: confirm the lockout threshold with security to TODO — then close the session
