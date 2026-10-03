---
tags: [case:edit--generate-in-scope-on-signal, skill:edit, sec:edit:usage, sec:edit:boundaries, sec:edit:sources-of-truth, sec:edit:session-start-every-mode, sec:edit:edit-discipline, sec:edit:modes, sec:edit:session-end-every-mode, sec:edit:self-learning, ref:create/project-config, ref:create/doc-corpus, ref:create/authoring-guide, sec:edit:decision-log, ref:edit/decision-log, sec:edit:draft-scaffolds, ref:edit/draft-scaffolds, ref:create/srd-procedures]
runs: 1
max_turns: 60
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.
  Before taking a scripted answer, write out in full, as your reply text, the
  message you would send the user at that point (every proposal with its
  location, before/after text and choices), then write the answer you take on a
  line of its own as `User: <answer>`, and only then continue. Never apply a
  change whose proposal you have not written out this way.

  Scripted answers (pick the one that fits the question):
  1. The first time the skill stops for an answer, whatever it asked: "The requirements are final now — please fill In Scope."
  2. To the candidate about token validation (signature or missing token): "Merge it with the token expiry candidate into one item: Validation of the Login Token signature and expiry on every API request."
  3. To the candidate about token expiry, if asked about it on its own: "Merge it with the token validation candidate, as I said."
  4. To the candidate about account lockout: "E — reword it to: Lockout of a user account after repeated failed sign-in attempts."
  5. To any other proposal or candidate: "Y".
  6. When the skill asks how to go on and In Scope is filled: "Close the session."
---

/srd:edit specs/login.md
