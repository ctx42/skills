---
name: skill-smith
description: >
  Authors new skills, audits existing ones against the repo's authoring
  standard, and measures whether a skill actually works. Use when asked to
  create, write, scaffold, review, improve, or benchmark/measure a skill. Not
  for a project's own README (readme-smith) or for recording session lessons
  (enhance-skills).
argument-hint: "[create|improve|measure] [<skill or description>]"
compatibility: Designed for Claude Code.
license: MIT
---

# skill-smith

## Usage

```
/skill-smith                  (default) infer create/improve/measure from the request; asks if ambiguous
/skill-smith create <desc>    create a whole new standard-compliant skill, evals first
/skill-smith improve <skill>  audit a skill against the standard, report, fix on confirmation
/skill-smith measure <skill>  A/B-benchmark the skill's eval scenarios and test triggering
```

Pick the mode from `$1`, or infer it from the user's prose when `$1` is empty:

- create — the user describes a new capability to package as a skill.
- improve — the user names an existing skill to review or upgrade.
- measure — the user wants proof a skill works, not an opinion that it does.

If the mode stays ambiguous, ask one question: create, improve, or measure?

The rest of `$ARGUMENTS` is the target — a description (create) or a skill name
or path (improve, measure).

Sources of truth:

- `standards.md` (eager in create and improve; unused by measure) — the
  authoring ruleset. Every decision defers to it.
- `CONTRIBUTING.md` (on-demand: placing, naming, cataloging, renaming, or
  retiring a skill) — repo mechanics. Follow it; never restate it.
- `evals/evals.json` (on-demand: measure mode, and when auditing this skill's
  own evals) — this skill's eval scenarios.
- `references/measuring.md` (on-demand: measure mode) — the A/B protocol.

Report tersely in every mode: no preamble or narration; state each fact once;
don't restate output the user can already see.

## Create mode

Build a complete, standard-compliant skill. Copy this checklist and tick it off:

```
- [ ] 1. Scope    — one job, its triggers, its plugin group
- [ ] 2. Name     — per standards.md, confirmed with the user
- [ ] 3. Evals    — evals/evals.json, written before the body
- [ ] 4. SKILL.md — the smallest body that passes them, plus ## Usage
- [ ] 5. Validate — fresh-context run, fix, repeat, then lint clean
- [ ] 6. Place    — <group>/skills/<name>/ + catalog docs
```

1. Scope it. Settle the one job this skill does, the phrases that should
   trigger it, and its plugin group (`golang`, `srd`, `craft`, or a new one).
   Ask only what you cannot infer.

2. Name it per `standards.md` Frontmatter. Confirm the name with the user.

3. Write the evals first, into `evals/evals.json`. Push one hard task until it
   succeeds unaided, note what you had to supply, then encode that as a query
   plus its expected-behavior checks, per `standards.md` Evaluations. Broaden
   to more scenarios only once the first one passes. These evals are the spec
   the body must pass.

4. Write `SKILL.md` — the smallest dense imperative body that passes them.
   Open with a `## Usage` block per `standards.md`; the skill ships no
   `README.md`. Adopt the Claude-native affordances where they earn their
   place. Put the output-discipline line where the skill describes its output.
   Close with the `## Self-learning` block; `enhance-skills` owns its wording.

5. Validate, then loop. Run the evals in a **fresh subagent**, never in this
   session — this conversation already holds the intent and corrections the
   skill is supposed to carry on its own, so a dry-run here passes on context
   the real user will not have. Then:

   - It never triggers — strengthen the description, repeat.
   - It triggers but fails a check — fix the body, repeat.
   - Its value is in doubt — run Measure mode instead of another run.

   Watch how the subagent moved, not just whether it passed: a reference read
   every run belongs in the body, one never opened is dead weight
   (`standards.md` Observing real use).

   Move on only once every eval passes. Then run `./dev/lint-skills.sh` and
   clear every error.

6. Place it at `<group>/skills/<name>/` and update the catalog docs, both per
   `CONTRIBUTING.md`.

Output: the new skill files, the catalog diffs, one line naming the skill's job
and triggers, then a reminder to run `/reload-plugins`.

## Improve mode

Audit one named skill against the standard, report, then fix on confirmation.
Scope is the single skill named; audit a whole group only when asked.

```
- [ ] 1. Resolve — the skill directory and the files in scope
- [ ] 2. Read    — SKILL.md, evals/evals.json, every bundled file
- [ ] 3. Audit   — walk standards.md in Contents order
- [ ] 4. Report  — by severity, no edits yet
- [ ] 5. Fix     — on confirmation, then lint clean
```

1. Resolve the target. State the exact skill directory and the files in scope.
   If none was named, ask which one.

2. Read the target's `SKILL.md`, `evals/evals.json`, and every bundled file.
   Consult `CONTRIBUTING.md` only for the mechanics it owns.

3. Audit against `standards.md`. It is already loaded — walk its rule sections
   in Contents order instead of re-deriving them. Two checks get skipped most
   often:

   - Reference content. Apply the Body-conciseness tests to each reference's
     prose, not just its structure, and flag any step that eagerly loads a
     whole reference every run.
   - Output discipline. The body carries the terse-output line, and no step
     mandates framing or restating shown content.
   - Observed use, when the user brings a transcript. Score it against
     `standards.md` Observing real use rather than reading structure alone.

4. Report only. Make no edit before the user approves.

5. Fix on confirmation. Apply the approved findings and show the diffs. Run
   `./dev/lint-skills.sh` and clear every error. If the structure changed (a
   rename, new files), follow `CONTRIBUTING.md` and remind the user to run
   `/reload-plugins`.

Output: findings grouped by severity — Blocker / Should-fix / Nit. Each finding
names the file (and the line where it helps), the `standards.md` rule it breaks,
and the minimal fix. Close with a verdict — compliant or fix-first — then offer
to apply the fixes.

## Measure mode

Prove the skill earns its tokens instead of eyeballing it:

1. Load the target's `evals/evals.json` — it is already the rubric.
2. Run each scenario in two fresh subagents — skill loaded, skill not loaded.
3. Grade both legs blind, then score how often the description triggers.

Follow `references/measuring.md` for the protocol. Report the result table and
the verdict. Make no edit from a Measure run without confirmation.

## Related skills

- `grill-me` — run it first when a new skill's purpose or triggers are fuzzy;
  create mode assumes the scope is already settled.
- `enhance-skills` — owns the `## Self-learning` block create mode installs,
  and records lessons into skills after a run.
- `readme-smith` — owns project-level `README.md` files. Skills ship none.

## Self-application

`skill-smith` obeys its own standard. After changing this skill, re-audit it in
improve mode.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/craft/skill-smith.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
