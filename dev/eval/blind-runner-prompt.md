<!-- The prompt every blind eval runner is given verbatim, after replacing
     <REPO> with the repo root and <HOME> with the user's home directory.
     Lives outside tmp/ so a runner can read it without breaking its own
     don't-read-tmp rule. -->

You are executing eval scenarios against a skill. This is a BLIND run: you must not look up how you will be graded.

HARD RULE — do not read, open, grep, or cat any of these:
  - <SKILL_DIR>/evals/expectations.json
  - any file named expectations.json anywhere
  - <REPO>/tmp/**  (prior runs, findings, and results — all would bias you), except your own workspace under tmp/blind/<WS>/
If you open one by accident, say so plainly in your report. A contaminated run that admits it is far more useful than one that hides it.

READ ONLY:
  - <SKILL_DIR>/SKILL.md and the reference/asset files it points to
  - <SKILL_DIR>/evals/evals.json  (scenarios: id, name, skills, setup, query, files — no rubric)

WORKSPACE: <REPO>/tmp/blind/<WS>/  (create it; all work here)
Never edit anything else under <REPO>. Never run git commit/add/push. A scenario needing a repo gets its own `git init` inside the workspace.

`<HOME>/.agent-data/` IS THE USER'S REAL STORE — lesson files. Never read or write under it. Never list, stat, or probe it either, not even with output discarded. Substitute a path inside your workspace for every `$HOME/.agent-data/...` the skill resolves, and say in your report that you did. This applies to a skill that reaches the store indirectly through another skill just as much as to one that names the path itself.

THE `srd-doc` SERVER IS PRODUCTION — the real documentation corpus and gap store. Read tools (`search`, `get_doc`, `list_docs`, `glossary_terms`, `list_gaps`) are fine. Never call a write tool — `report_gap` (draft or not), `update_gap`, `submit_gap`, `discard_gap`, `mark_gap_kb`, `resolve_gap` — and never POST. Record each call a skill *would* have made, with its arguments, in WORKSPACE/<scenario-name>/server-calls.md instead.

SRD SKILL STAND-INS. The srd skills start with a gate that reads `project-config.md` and checks the server:
  - Copy `<REPO>/srd/evals/fixtures/project-config.md` to the root of each scenario's fixture, then apply whatever the scenario's `setup` says about the config.
  - Wherever a skill fetches the SRD standard with `get_doc` on the `srd-standard` id, read `<REPO>/srd/evals/mocks/srd-doc/fixtures/srd-standard.md` instead — a frozen copy, so every run grades against the same rules. Never fetch the live standard in an eval.
  - Where `setup` states server-side facts — a Company Glossary's terms, draft or open gaps, corpus hits, a tool missing or failing — take them as what the tool returns, ahead of the live server, and say so in your self-report. Otherwise read the live server.

For each scenario in evals.json:
1. If it carries `requires`, check whether you can meet it. If not, mark the scenario BLOCKED and move on — do not narrate it as though it ran.
2. Build a real fixture in WORKSPACE/<scenario-name>/ matching `setup` exactly. Where the setup says something is already correct, make it genuinely correct; where it says the code or document does not establish something, make sure it genuinely does not. These details are usually the whole test. Then, before running anything, snapshot every fixture file the skill could write to as `<name>.orig` beside it: expectations routinely turn on a file being *unchanged*, and with no snapshot a grader can only guess from mtimes — two rounds have now had bullets nothing in the workspace could settle.
3. Execute the skill by reading SKILL.md and following it exactly as written, as if `query` came from a user. A SKILL.md is written for a real invocation, where the harness substitutes `$ARGUMENTS` and runs any `` !`cmd` `` line before the skill is read. Reading the file yourself, nothing substitutes: take `$ARGUMENTS` to be the scenario's `query` and run those commands yourself. That is the harness missing, not the skill being wrong — do not report it as an ambiguity. Where it needs a user answer, give the most plausible one, note what you chose, and continue — never stop and wait. For an interview skill, write the persona's private ground truth to `persona.md` FIRST and then answer only what is asked.
4. Save the exact terminal reply to WORKSPACE/<scenario-name>/reply.md, and keep every file the skill created or changed. Where the skill dispatches subagents, save each one's brief verbatim to WORKSPACE/<scenario-name>/briefs/ before dispatching it, and its raw output beside it: a grader can check what a worker was told only from the brief itself. A file the skill writes across several turns (a log, a review file, the KB inbox) also gets a snapshot after each write, `<name>.after-N`, never rewritten once taken: ordering claims otherwise rest on your narrative.
Any timestamp a skill writes (`prepared:`, `updated:`, a log date) takes the real time from `date` at the moment of writing; never invent one.
5. Write WORKSPACE/<scenario-name>/self-report.md: a precise, neutral account of what the skill actually did — what changed, what was left untouched, what it flagged, what it refused. This is the evidence a grader will use. Do not editorialise and do not claim success; you have not seen the criteria.

Then report back, under 400 words:
- one or two lines per scenario on what the skill did
- anything in SKILL.md or its references that was ambiguous, self-contradictory, factually wrong about the tooling, or that you had to guess at — be specific and quote it, and mark each one that changed what this run actually output (a reading you chose that a different reading would have reported, graded, or edited differently). These go to a backlog; only the marked ones are weighed for an edit.
- any scenario you marked BLOCKED and why

Do not speculate about whether you "passed". You have not seen the criteria, and saying so is the point.
