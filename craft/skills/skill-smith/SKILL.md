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

- **Create** — the user describes a new capability, workflow, or knowledge area
  to package as a skill.
- **Improve** — the user names an existing skill (path or name) to review or
  upgrade.

If the request is ambiguous, ask one question: create new or improve existing?

Sources of truth (read once per run):
- `standards.md` — the authoring ruleset (quality + this
  repo's strict-portable frontmatter rules). Every decision defers to it.
- `CONTRIBUTING.md` — authoritative for repo mechanics: where skills live (under
  a plugin group's `skills/` dir), naming, the catalog-doc update list, the
  plugin dev loop, retiring. Do not duplicate it; follow it.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/craft/skill-smith.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.

## Create mode

Forge a complete, standard-compliant skill end-to-end.

### Workflow

1. **Scope it.** From the user's description, settle: the one job this skill
   does, its trigger phrases (for the description), create-vs-knowledge nature,
   and which plugin group it belongs to (`golang`, `srd`, `craft`,
   or a new group). Ask only what you cannot infer.
2. **Read** `standards.md` and the relevant parts of `CONTRIBUTING.md`.
3. **Name it.** Lowercase-hyphen, gerund or short verb, equals the dir name, no
   reserved words / org or vendor prefix. Confirm the name with the user.
4. **Evals first.** Before writing the body, derive **≥ 3** scenarios from where
   the agent falls short *without* the skill — run the task unaided, note what
   fails, and encode each failure as a request + expected-behavior checks (**≥ 1
   asserting terse output**). These evals are the spec the body must pass, not a
   closing formality.
5. **Write `SKILL.md`.** Strict-portable frontmatter (`name` + `description`,
   plus allowed optional) — non-standard fields break portability. Write the
   **minimum** dense imperative body that passes the evals; it's always-loaded
   token cost, so cut anything that doesn't raise success rate, and keep it under
   ~500 lines. Use progressive disclosure — push large reference material into
   sibling files linked one level deep; reference content obeys the body's
   conciseness test and is consulted on demand, never preloaded. Carry the
   output-discipline line (`standards.md`) where the skill describes its output.
6. **Write `README.md`.** Concise usage + when-to-use, and an `## Evaluations`
   section holding the step-4 scenarios.
7. **Validate & refine.** Dry-run the skill against its evals; where it
   struggles, fix the skill (strengthen the description first if it fails to
   trigger) and repeat until the evals pass. Then run `./dev/lint-skills.sh` and
   clear every error.
8. **Update catalog docs** per CONTRIBUTING.md's Documentation list (skill
   README, category README, top-level README, `STRUCTURE.md`, `AGENTS.md`, and
   `ONBOARDING.md` if relevant).
9. **Place & load.** The skill lives at `<group>/skills/<name>/`. If it starts a
   **new** group, add that group's `.claude-plugin/plugin.json` and a
   marketplace entry (existing groups need neither — the default `skills/` scan
   picks the skill up). Show the files and doc updates, then tell the user to run
   `/reload-plugins` (or re-launch with `--plugin-dir ./<group>`) to load it.

### Output

The new skill files, the catalog diffs, the evals, and a one-line statement of
the skill's job and triggers. Then the reload reminder.

## Improve mode

Audit one named skill against the standard, report, then fix on confirmation.
Reasoning only until the user approves — no edits during the audit.

Default scope is the **single** skill named. Audit a whole category only if the
user asks.

### Workflow

1. **Resolve the target.** State the exact skill dir and files in scope. If the
   user named no skill, ask which one.
2. **Read** `standards.md`, `CONTRIBUTING.md`, then the target's `SKILL.md`,
   `README.md`, and any bundled files.
3. **Audit** against the standard, in this order:
   - **Frontmatter** — strict-portable set only; `name` equals dir name; no
     forbidden/misspelled fields (e.g. `user_invocable`); description is third
     person, what + when, specific triggers.
   - **Body** — conciseness (redundant explanation, > ~500 lines), consistent
     terms, no time-sensitive info, right degree of freedom.
   - **Output discipline** — body carries the terse-output line; output/report
     steps mandate no framing and no restating of shown content; payload stated
     in full. Flag duplicate or repeating summaries.
   - **Structure** — progressive disclosure, references one level deep, files
     named for content, ToC on long files.
   - **Reference content** — read each reference, not just its structure: apply
     the body's conciseness test to it (cut what the model already knows), flag
     entries that restate the rule or file they key to or that collapse to one
     shared principle, and flag any workflow step that reads a whole reference
     eagerly each run instead of consulting it on demand.
   - **Workflows** — clear steps / checklist, feedback loops where quality
     matters; scripts solve-not-punt with no voodoo constants.
   - **Evals** — `README.md` has `## Evaluations` with ≥ 3 scenarios.
4. **Report only.** Do not edit yet.
5. **Fix on confirmation.** Apply the approved findings, show diffs, then run
   `./dev/lint-skills.sh` and clear any error. If structure changed (rename, new
   files) follow CONTRIBUTING.md and remind the user to run `/reload-plugins`.

### Output

Group findings by severity: **Blocker / Should-fix / Nit**. Each finding:
- `file` (and line if useful) — the problem in one line.
- The rule from `standards.md` it violates.
- A minimal suggested fix.

End with a verdict (compliant / fix-first) and per-severity counts. Then offer
to apply the fixes.

## Self-application

`skill-smith` obeys its own standard: strict-portable frontmatter, a README with
≥ 3 evals, references one level deep (`standards.md`). When you change this
skill, re-audit it in improve mode.

Report tersely in both modes: no preamble or narration; state each fact once;
don't restate output the user can already see.
