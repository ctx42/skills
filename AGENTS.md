# AGENTS.md

Guide for AI agents working in this repository.

This repository is a collection of for the reusable skills use by both Grok
and Claude. Skills ship as **Claude Code plugins**, grouped into `golang`,
`srd`, and `craft`. Each skill is a directory under a group's `skills/`
folder with a `SKILL.md` (the prompt) and a `README.md` (human usage guide).

## Golden Rules

1. **Edit only in this repo.** The installed copies under
   `~/.claude/plugins/cache/` (and Grok's cache) are generated; never edit there.
2. **Keep `SKILL.md` token-optimized.** These prompts are loaded into context.
   Prefer short, dense, imperative wording over prose.
3. **Skills live under a group.** A skill's path is `<group>/skills/<name>/`.
   Adding one to an existing group needs no marketplace edit — the default
   `skills/` scan finds it. A new group needs its own `.claude-plugin/plugin.json`
   and a `marketplace.json` entry.
4. **Reference siblings relatively.** Skills in the same plugin resolve each other
   as `../sibling/...` (they are cached together). Cross-plugin file references do
   not resolve — keep interdependent skills in one group.
5. **Lint before committing.** Run `./dev/lint-skills.sh` after editing any skill; it
   checks the mechanical parts of the authoring standard and the marketplace
   wiring, and exits non-zero on any error.

## Dev loop

Load a group straight from the repo and reload after edits — no reinstall:

```bash
claude --plugin-dir ./srd      # repeat the flag for more groups
# …edit a SKILL.md…
/reload-plugins                       # live pick-up
/srd:system-check           # test (skills are namespaced /group:skill)
```

## Active Skill Catalog

### golang

- `style` — The enforced Go style guide. Has a `Production` section (for
  `*.go`) and a `Test` section (for `*_test.go`). Read it before writing or
  editing any Go file and follow it. It is the canonical, terse ruleset.
- `review` — The done-time review entrypoint. Run it after edits and a
  feature are complete: it checks the changed Go code against the `style`
  rules, the deeper criteria in `review/rules.md`, and general correctness
  (bugs, edge cases, error handling). Reasoning only — it does not run tools.
  It also owns rule editing: a free-form suggestion becomes a terse rule in
  `style`, or `/review learn` mines the current editing session's feedback into
  rules (use it instead of hand-editing `style`).
- `cover` — Improves test coverage. Executing skill: it runs `go test
  -coverprofile`, edits/creates `*_test.go`, and re-runs to verify. Governing
  rule: a function's coverage counts only from its own style-named direct
  test, measured in isolation on that function's own lines. Targets a single
  function, a line, a file, a package, or a module; honors `max_tests`,
  `packages`, `include=all`.
- `reshape` — Consumer-driven API review. Given a library the project depends
  on, it maps every call site, diagnoses the friction, and proposes ranked,
  impact-scored changes to that **library's** API that would simplify the
  consuming code. Reasoning only — read-only, edits nothing. Brainstorms across
  a broad archetype catalog (`reshape/references/change-catalog.md`) and detects
  whether the library is locally editable (concrete diffs) or external (public
  surface). Honors `max`.

### srd

- `create` — Author a brand-new Software Requirement Document (SRD) to the
  SRD standard. Interviews the user along the fixed SRD spine, proposes
  requirement groups and prefixes, reuses the shared glossary, drafts the
  document from a template, and self-checks the draft against the standard's
  rules (`references/srd-standard.md`) before writing the file. Authoring only.
- `review` — Read-only review of an SRD someone else wrote, against the same
  SRD standard (reused from `../create/references/`, not duplicated). Writes
  findings to a `<srd>.review.md` beside the source — grouped by section, each
  citing a rule id and tagged blocker / major / minor. Never edits the source.
- `edit` — The write counterpart to `review`: edits an existing SRD in
  place against the same SRD standard. Every session starts with an approval gate
  that governs id rules. Proposes one change at a time with before/after, applies
  only on confirmation, and re-validates after each. Writes no file but the SRD.
- `system-check` — Reviews an SRD for build-readiness from the implementing
  engineer's seat. Delegates standard/logic/consistency checks to `review`,
  then adds a system-knowledge layer confronting the SRD against a curated,
  growing `memory.md` (see [STRUCTURE.md](./STRUCTURE.md#system-check-memory)
  for where memory lives). Merges both into one colleague-voice
  `<srd>.questions.md`, walked one question at a time. Modes: review (default),
  memory.

### craft

- `cm` — Conventional commit messages with kernel-style bodies.
- `grill-me` — Relentless planning interview; walks the whole design tree before
  any code is written.
- `skill-smith` — Author new skills and improve existing ones. Two modes: create
  (scaffold a full skill end-to-end under a group) and improve (audit a named
  skill against `craft/skills/skill-smith/standards.md`, then fix on
  confirmation). Owns the authoring standard; defers to this file and
  CONTRIBUTING.md for repo mechanics.
- `readme-smith` — Author and improve a project's `README.md`. Two modes: create
  (scan the repo, ask only the gaps, draft to a distilled house structure) and
  improve (audit an existing README, report by severity, fix on confirmation).
  Structure and style come from `craft/skills/readme-smith/references/template.md`;
  never fabricates facts and runs the install/quickstart commands it ships.

## More Detail

- [README.md](./README.md) — overview, install, and dev loop
- [STRUCTURE.md](./STRUCTURE.md) — directory map and the plugin model
- [CONTRIBUTING.md](./CONTRIBUTING.md) — how to add, rename, and retire skills
- [ONBOARDING.md](./ONBOARDING.md) — machine setup for Grok and Claude
