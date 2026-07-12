# AGENTS.md

Guide for AI agents working in this repository.

This repository is a collection of reusable skills used by both Grok
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

One line per skill for orientation; each skill's `SKILL.md` description is the
source of truth.

### golang

- `style` — the enforced Go style rules (Production + Test); read before any
  `.go` edit.
- `review` — done-time review of finished Go code; also owns adding and
  learning style rules.
- `cover` — raises Go test coverage per function, measured from direct tests
  only.
- `reshape` — proposes consumer-driven API changes to a library the project
  uses; read-only.

### srd

- `create` — interviews, drafts, and self-checks a new SRD; owns the shared
  SRD references.
- `review` — read-only SRD review; findings go to `<srd>.review.md` beside the
  source.
- `edit` — edits an existing SRD in place, one confirmed change at a time.
- `system-check` — build-readiness questions for an SRD; owns
  `<srd>.questions.md` and the platform-knowledge memory.

### craft

- `cm` — Conventional Commit messages with kernel-style bodies, from the diff
  only.
- `grill-me` — relentless planning interview until shared understanding.
- `plan-smith` — writes and tracks an implementation plan (checkbox items,
  Y/N/X status table).
- `skill-smith` — authors and audits skills; owns the authoring standard
  (`standards.md`).
- `readme-smith` — authors and audits project READMEs against its
  `references/template.md`.
- `enhance-skills` — harvests session corrections into per-skill lessons;
  retrofits the `## Self-learning` block.

## More Detail

- [README.md](./README.md) — overview, install, and dev loop
- [STRUCTURE.md](./STRUCTURE.md) — directory map and the plugin model
- [CONTRIBUTING.md](./CONTRIBUTING.md) — how to add, rename, and retire skills
- [ONBOARDING.md](./ONBOARDING.md) — machine setup for Grok and Claude
