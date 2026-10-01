<!-- The prompt every blind eval runner is given verbatim. Lives outside tmp/
     so a runner can read it without breaking its own don't-read-tmp rule. -->

You are executing eval scenarios against a skill. This is a BLIND run: you must not look up how you will be graded.

HARD RULE — do not read, open, grep, or cat any of these:
  - <SKILL_DIR>/evals/expectations.json
  - any file named expectations.json anywhere
  - /home/thor/ws/ctx42/skills/tmp/**  (prior runs, findings, and results — all would bias you), except your own workspace under tmp/blind/<WS>/
If you open one by accident, say so plainly in your report. A contaminated run that admits it is far more useful than one that hides it.

READ ONLY:
  - <SKILL_DIR>/SKILL.md and the reference/asset files it points to
  - <SKILL_DIR>/evals/evals.json  (scenarios: id, name, skills, setup, query, files — no rubric)

WORKSPACE: /home/thor/ws/ctx42/skills/tmp/blind/<WS>/  (create it; all work here)
Never edit anything else under /home/thor/ws/ctx42/skills. Never run git commit/add/push. A scenario needing a repo gets its own `git init` inside the workspace.

`/home/thor/.agent-data/` IS THE USER'S REAL STORE — lesson files, doc-gap buffers, session state. Never read or write under it. Substitute a path inside your workspace for every `$HOME/.agent-data/...` the skill resolves, and say in your report that you did. This applies to a skill that reaches the store indirectly through another skill just as much as to one that names the path itself: the run that leaked a fixture buffer into the real store was `srd:review`, which never mentions `.agent-data` and delegates to a skill that does.

THE `srd-doc` SERVER ON localhost:7777 IS PRODUCTION — the real INFRAPORT corpus and gap store. `GET` is fine. Never POST, never resolve, never write. Capture what a skill *would* have filed into your workspace instead.

For each scenario in evals.json:
1. If it carries `requires`, check whether you can meet it. If not, mark the scenario BLOCKED and move on — do not narrate it as though it ran.
2. Build a real fixture in WORKSPACE/<scenario-name>/ matching `setup` exactly. Where the setup says something is already correct, make it genuinely correct; where it says the code or document does not establish something, make sure it genuinely does not. These details are usually the whole test. Then, before running anything, snapshot every fixture file the skill could write to as `<name>.orig` beside it: expectations routinely turn on a file being *unchanged*, and with no snapshot a grader can only guess from mtimes — two rounds have now had bullets nothing in the workspace could settle.
3. Execute the skill by reading SKILL.md and following it exactly as written, as if `query` came from a user. A SKILL.md is written for a real invocation, where the harness substitutes `$ARGUMENTS` and runs any `` !`cmd` `` line before the skill is read. Reading the file yourself, nothing substitutes: take `$ARGUMENTS` to be the scenario's `query` and run those commands yourself. That is the harness missing, not the skill being wrong — do not report it as an ambiguity. Where it needs a user answer, give the most plausible one, note what you chose, and continue — never stop and wait. For an interview skill, write the persona's private ground truth to `persona.md` FIRST and then answer only what is asked.
4. Save the exact terminal reply to WORKSPACE/<scenario-name>/reply.md, and keep every file the skill created or changed. Where the skill dispatches subagents, save each one's brief verbatim to WORKSPACE/<scenario-name>/briefs/ before dispatching it, and its raw output beside it: a grader can check what a worker was told only from the brief itself.
5. Write WORKSPACE/<scenario-name>/self-report.md: a precise, neutral account of what the skill actually did — what changed, what was left untouched, what it flagged, what it refused. This is the evidence a grader will use. Do not editorialise and do not claim success; you have not seen the criteria.

Then report back, under 400 words:
- one or two lines per scenario on what the skill did
- anything in SKILL.md or its references that was ambiguous, self-contradictory, factually wrong about the tooling, or that you had to guess at — be specific and quote it, and mark each one that changed what this run actually output (a reading you chose that a different reading would have reported, graded, or edited differently). These go to a backlog; only the marked ones are weighed for an edit.
- any scenario you marked BLOCKED and why

Do not speculate about whether you "passed". You have not seen the criteria, and saying so is the point.
