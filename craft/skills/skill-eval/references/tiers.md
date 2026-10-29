# Eval tiers and loop

Which tier tests what, what each costs, and when the loop stops. Work order
and long runs: [running.md](running.md); mistakes past runs paid for:
[pitfalls.md](pitfalls.md).

## Contents

- [Two agents](#two-agents)
- [Tiers](#tiers)
- [The eval loop](#the-eval-loop)
- [Real stores](#real-stores)

## Two agents

Run them with two agents, never one: a runner that sees `evals.json` and never
`expectations.json`, then a grader that sees `expectations.json` and never
`SKILL.md`. Ask the runner what in the instructions was ambiguous or had to be
guessed at — in the first full round that question found more defects than the
pass counts did — but its answer is a backlog, not a work list (see *The eval
loop* below).

**What to distrust in a result.**

- *One agent doing both jobs.* Its pass counts mean "these instructions are
  followable", not "an uninformed agent follows them".
- *`"files": []`.* The runner then authors the corpus it is graded on. A real
  fixture under `assets/` is stronger; `srd:review`'s `flawed-srd.md` is the
  model. Its scenario's bullets are the baseline of every defect it plants:
  plant one only with its bullet, and add any defect a run finds that no
  bullet lists. A fixture never names its expectations file — a blind runner
  reads it.
- *An interview skill.* `grill-me`, `srd:create`, `srd:edit` need someone to
  play the user, and one agent playing both sides is a weak test. Have it
  write the persona's ground truth down first and say where it was generous.
- *A pre-fix run graded against post-fix expectations.* Editing a scenario or
  an expectation after a run invalidates that run's verdict on it. Re-run, or
  tell the grader which bullets the edit reaches.

## Tiers

**Tiers.** The routine check after any edit is free and takes seconds; the
paid routine checks cost cents and finish in a minute or two.
`scripts/eval-routine.sh` runs tiers 1–4 in one go — lint, then probes,
triggers, and the hunt in parallel — for ~\$0.15 and ~2 min per changed skill:

1. *Lint and contracts* (`scripts/lint-skills.sh`, which runs
   `scripts/eval-check.py`; free, seconds). Each skill's `evals/contract.json`
   lists its high-stakes rules as phrases its text must keep; an edit that
   deletes, weakens, or contradicts one fails here, named. The same check
   re-runs the case generators, catches a fixture or mock rename that missed
   one side, checks `dev/eval/triggers.json`, and fails an expectations bullet
   that no grader, probe (`"bullets": ["<scenario>#b<N>"]`), or `blind_only`
   entry accounts for. Mechanical edits (fixtures, mocks, ids, generators)
   stop here: they never need a model run.
2. *Probes* (`scripts/eval-probe.py`; ~\$0.02 and ~20 s per changed skill). Each
   skill's `evals/probes.json` asks one question per rule most likely to
   regress — the skill text as system prompt, a prepared situation, a short
   answer graded by regex, on haiku. A skill's probes go in one batched call
   without thinking; a miss is re-asked alone three times with thinking, so
   only FAIL (0/3) and SPLIT survive. Answers are cached by input. Run after
   any behaviour change, without asking. A new high-stakes rule gets a
   contract rule and a probe in the same change. Every probe carries a class
   from `--baseline --write`: a `prior` probe (it passes with no skill text)
   tests the model, not the skill, and fails lint — make the skill and the
   default disagree, or delete it. A probe for a fix must FAIL at the pre-fix
   ref (`--against <ref>`) and pass now.
3. *Hunt* (`scripts/eval-hunt.py`; ~\$0.10 and ~2 min per changed skill). Sonnet
   proposes situations the diff's added lines let an agent read two ways,
   quotes checked verbatim; each is asked three times on haiku and only a
   SPLIT is reported, as a draft probe. Run after a behaviour change.
4. *Triggers* (`scripts/eval-triggers.py`; ~\$0.04, ~20 s). Routes every request
   in `dev/eval/triggers.json` against all skill descriptions plus real
   distractors. Run after a description changes.
5. *Agent-run cases* (`scripts/eval-changed.sh --audit --model default`;
   ~\$0.25–0.80 a case, up to minutes). Full sessions on scripted fixtures with
   mocked MCP servers ([native-cases.md](native-cases.md)); `needs-shell` cases
   run through `scripts/eval-shell.mjs` instead. A manual audit only, when the
   user asks; never the gate on a change. Cases run on the default model
   (`--model default`), whose first verdict stands; skip the script's sonnet
   pass. A pass is recorded in a ledger keyed by everything the case depends on,
   and the run stops at the first usage-limit cut-off (exit 3) — re-run the same
   command after the reset. Verify a grader fix offline with
   `scripts/eval-regrade.py <trace>`, never by a paid re-run.
6. *Blind round* (the repo's blind-runner and grader prompts, handed over
   verbatim). An audit before a release or after a large refactor, never the
   gate on an ordinary change; the release audit also runs
   `scripts/eval-probe.py --compare haiku,sonnet,opus` (~\$1–2) and triages the
   probes the models disagree on.

## The eval loop

**The eval loop.** A blind round costs hundreds of thousands of tokens, and a
runner always finds something new to doubt, so the loop ends only on these
rules:

- Edit a skill only for a graded FAIL, a disagreement measured on identical
  input (workers or runs splitting on the same bytes), or a miss on real code
  the user reports. Anything else — a runner's ambiguity list included — goes
  to `tmp/eval-backlog.md` and triggers no re-run.
- Before any blind round, state its scope and rough cost and get the user's
  go-ahead.
- A behaviour change runs the probes and the hunt, never the agent-run suite;
  tiers 5–6 run only on the user's request, and only the failing or cut-off
  cases are re-run.
- One fix-and-re-run per FAIL; a bullet that fails again after its fix goes to
  the user as a design question, not another rewording.
- A hunt split may drive one fix; a split the next hunt finds on lines that
  fix added goes to `tmp/eval-backlog.md`, not another edit — each fix gives
  the hunter new text to doubt, and chasing it never ends. A split with no
  clear intended answer goes there too, as a question.
- At most two rounds per change unless the user raises it; a round with every
  gradable bullet PASS and no measured split ends the loop — no confirmation
  round, no new scenario for a guard that has never fired.
- Freeze `expectations.json` while a loop runs: batch the defects a grader
  finds and apply them after it ends, so no round grades a moved target.
- The go-ahead for a round covers it end to end, the re-runs its fixes need
  included, within its cost cap: finish without asking again, report once, and
  batch the real design questions at the end. At the cap, stop and list what did
  not run as open.

Without these rules, three consecutive `go:style` rounds passed every bullet,
yet cost about a million tokens, because each runner's new ambiguity list was
treated as the next round's work and nothing measured what those edits bought.

## Real stores

`$HOME/.agent-data/` holds the user's real lesson files, and a live server a
skill calls may be production. Tell every eval agent so: redirect every
`$HOME/.agent-data` path a skill resolves into the run's workspace, and call
only a server's read tools.
