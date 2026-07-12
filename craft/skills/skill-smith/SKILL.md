---
name: skill-smith
description: >
  Authors new skills and audits existing ones against the repo's authoring
  standard. Use when asked to create, write, scaffold, review, or improve a
  skill.
license: MIT
---

# skill-smith

Forge and repair skills. Pick the mode from the request:

- Create — the user describes a new capability, workflow, or knowledge area to
  package as a skill.

- Improve — the user names an existing skill (path or name) to review or
  upgrade.

If the request is ambiguous, ask one question: create new or improve existing?

Sources of truth:

- `standards.md` (eager) — the authoring ruleset; every decision defers to it.

- `CONTRIBUTING.md` (on-demand: repo mechanics) — skill placement, naming, the
  catalog-doc list, dev loop, and retiring. Follow it; never duplicate it.

## Create mode

Forge a complete, standard-compliant skill end-to-end.

1. Scope it. Settle the one job this skill does, its trigger phrases, whether
   it creates or packages knowledge, and its plugin group (`golang`, `srd`,
   `craft`, or a new one). Ask only what you cannot infer.

2. Read `standards.md` and the relevant parts of `CONTRIBUTING.md`.

3. Name it. Lowercase-hyphen, gerund or short verb, equals the dir name, no
   reserved words or vendor prefix. Confirm the name with the user.

4. Evals first. Derive ≥ 3 scenarios from where the agent falls short without
   the skill: run the task unaided, note what fails, encode each failure as a
   request + expected-behavior checks (≥ 1 asserting terse output). These evals
   are the spec the body must pass.

5. Write `SKILL.md`. The minimum dense imperative body that passes the evals,
   per `standards.md` — portable frontmatter, token economy, ≤ ~500
   lines, progressive disclosure, and the output-discipline line where the
   skill describes its output.

6. Write `README.md`. Concise usage + when-to-use, and an `## Evaluations`
   section holding the step-4 scenarios.

7. Validate & refine. Dry-run against the evals; where it struggles, fix the
   skill (strengthen the description first if it fails to trigger) and repeat.
   Then run `./dev/lint-skills.sh` and clear every error.

8. Update catalog docs per CONTRIBUTING.md's Documentation list.

9. Place & load. The skill lives at `<group>/skills/<name>/`. A new group also
   needs its `.claude-plugin/plugin.json` and a marketplace entry (existing
   groups need neither). Show the files and doc updates, then tell the user to
   run `/reload-plugins` to load it.

Output: the new skill files, the catalog diffs, the evals, and a one-line
statement of the skill's job and triggers. Then the reload reminder.

## Improve mode

Audit one named skill against the standard, report, then fix on confirmation.
Reasoning only until the user approves — no edits during the audit. Default
scope is the single skill named; audit a whole category only if asked.

1. Resolve the target. State the exact skill dir and files in scope. If none
   was named, ask which one.

2. Read `standards.md`, `CONTRIBUTING.md`, then the target's `SKILL.md`,
   `README.md`, and any bundled files.

3. Audit against `standards.md` — it is loaded, so walk its rule sections (see
   its Contents) in order rather than re-deriving them. Two checks are easy to
   skip:

   - Reference content — read each reference's prose, not just its structure;
     flag entries that restate the rule they key to or collapse to one shared
     principle, and any step that reads a whole reference eagerly each run.

   - Output discipline — the body carries the terse-output line and no step
     mandates framing or restating shown content.

4. Report only. Do not edit yet.

5. Fix on confirmation. Apply the approved findings, show diffs, then run
   `./dev/lint-skills.sh` and clear any error. If structure changed (rename,
   new files) follow CONTRIBUTING.md and remind the user to run
   `/reload-plugins`.

Output: group findings by severity — Blocker / Should-fix / Nit. Each finding
names the file (and line if useful), the `standards.md` rule it violates, and a
minimal fix. End with a verdict (compliant / fix-first) and per-severity counts,
then offer to apply the fixes.

## Self-application

`skill-smith` obeys its own standard. When you change this skill, re-audit it in
improve mode.

Report tersely in both modes: no preamble or narration; state each fact once;
don't restate output the user can already see.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/craft/skill-smith.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
