---
name: skill-smith
description: >
  Authors new skills, audits existing ones against the repo's authoring
  standard, and measures whether a skill actually works. Use when asked to
  create, write, scaffold, review, improve, or benchmark/measure a skill.
argument-hint: "[create|improve|measure] [<skill or description>]"
compatibility: Claude Code; skills here ship as Claude Code plugins.
license: MIT
---

# skill-smith

Pick the mode from `$1`, or infer it from the user's prose when `$1` is empty:

- create — the user describes a new capability to package as a skill.
- improve — the user names an existing skill to review or upgrade.
- measure — the user wants proof a skill works, not an opinion that it does.

If the mode stays ambiguous, ask one question: create, improve, or measure?

The rest of `$ARGUMENTS` is the target — a description (create) or a skill name
or path (improve, measure).

Sources of truth:

- `standards.md` (eager) — the authoring ruleset. Every decision defers to it.
- `CONTRIBUTING.md` (on-demand: placing, naming, cataloging, renaming, or
  retiring a skill) — repo mechanics. Follow it; never restate it.

Report tersely in every mode: no preamble or narration; state each fact once;
don't restate output the user can already see.

## Create mode

Build a complete, standard-compliant skill. Copy this checklist and tick it off:

```
- [ ] 1. Scope     — one job, its triggers, its plugin group
- [ ] 2. Name      — per standards.md, confirmed with the user
- [ ] 3. Evals     — written before the body
- [ ] 4. SKILL.md  — the smallest body that passes them
- [ ] 5. README.md — Usage block + those evals
- [ ] 6. Validate  — dry-run, fix, repeat, then lint clean
- [ ] 7. Place     — <group>/skills/<name>/ + catalog docs
```

1. Scope it. Settle the one job this skill does, the phrases that should
   trigger it, and its plugin group (`golang`, `srd`, `craft`, or a new one).
   Ask only what you cannot infer.

2. Name it per `standards.md` Frontmatter. Confirm the name with the user.

3. Write the evals first. Run the task unaided and note what fails. Encode each
   failure as a request plus its expected-behavior checks, per `standards.md`
   Evaluations. These evals are the spec the body must pass.

4. Write `SKILL.md` — the smallest dense imperative body that passes them.
   Adopt the Claude-native affordances where they earn their place. Put the
   output-discipline line where the skill describes its output. Close with the
   `## Self-learning` block; `enhance-skills` owns its wording.

5. Write `README.md` per `standards.md` README structure, carrying the step-3
   scenarios under `## Evaluations`.

6. Validate, then loop. Dry-run the skill against its own evals:

   - It never triggers — strengthen the description, repeat.
   - It triggers but fails a check — fix the body, repeat.
   - Its value is in doubt — run Measure mode instead of another dry-run.

   Move on only once every eval passes. Then run `./dev/lint-skills.sh` and
   clear every error.

7. Place it at `<group>/skills/<name>/` and update the catalog docs, both per
   `CONTRIBUTING.md`.

Output: the new skill files, the catalog diffs, one line naming the skill's job
and triggers, then a reminder to run `/reload-plugins`.

## Improve mode

Audit one named skill against the standard, report, then fix on confirmation.
Scope is the single skill named; audit a whole group only when asked.

1. Resolve the target. State the exact skill directory and the files in scope.
   If none was named, ask which one.

2. Read the target's `SKILL.md`, `README.md`, and every bundled file. Consult
   `CONTRIBUTING.md` only for the mechanics it owns.

3. Audit against `standards.md`. It is already loaded — walk its rule sections
   in Contents order instead of re-deriving them. Two checks get skipped most
   often:

   - Reference content. Apply the Body-conciseness tests to each reference's
     prose, not just its structure, and flag any step that eagerly loads a
     whole reference every run.
   - Output discipline. The body carries the terse-output line, and no step
     mandates framing or restating shown content.

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

1. Turn the target's README scenarios into a pass/fail rubric.
2. Run each scenario in two fresh subagents — skill loaded, skill not loaded.
3. Grade both legs blind, then score how often the description triggers.

Follow `references/evals.md` for the protocol. Report the result table and the
verdict. Make no edit from a Measure run without confirmation.

## Self-application

`skill-smith` obeys its own standard. After changing this skill, re-audit it in
improve mode.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/craft/skill-smith.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
