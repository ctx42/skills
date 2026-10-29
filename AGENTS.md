# AGENTS.md

Guide for AI agents working in this repository.

This repository is a collection of reusable skills for Claude. Skills ship as
**Claude Code plugins**, grouped into `go`, `srd`, `craft`, and `web`. A
fifth plugin, `notify`, ships desktop-attention hooks and no skills. Each skill
is a directory under a group's `skills/` folder with a `SKILL.md` (the prompt,
including its `## Usage` block), an `evals/evals.json` (its eval scenarios), an
`evals/expectations.json` (how each is graded — separate so a run can be
given a scenario without its rubric), an `evals/contract.json` (its high-stakes
rules as phrases the text must keep) and an `evals/probes.json` (one cached
question per rule likely to regress).
Skills ship no `README.md`; the repo-level one orients humans.

## Golden Rules

1. **Edit only in this repo.** The installed copies under
   `~/.claude/plugins/cache/` are generated; never edit there.
2. **Keep `SKILL.md` token-optimized.** These prompts are loaded into context.
   Prefer short, dense, imperative wording over prose. When an edit pushes a
   `SKILL.md` past the lint's token aim, move a section whose trigger is a
   condition (a mode, a claim type) into `references/<name>.md` and leave a
   pointer plus its one-line rule; never cut settled rules to make room.
3. **Skills live under a group.** A skill's path is `<group>/skills/<name>/`.
   Adding one to an existing group needs no marketplace edit — the default
   `skills/` scan finds it. A new group needs its own `.claude-plugin/plugin.json`
   and a `marketplace.json` entry. Never add a skill to `notify` — it is a
   hooks-only plugin.
4. **Reference siblings relatively.** Skills in the same plugin resolve each other
   as `../sibling/...` (they are cached together). Cross-plugin file references do
   not resolve — keep interdependent skills in one group.
5. **Lint before committing.** Run `./dev/lint-skills.sh` after editing any skill; it
   checks the mechanical parts of the authoring standard and the marketplace
   wiring, and exits non-zero on any error.
6. **Confirm a behaviour change with `/craft:skill-eval run`** or
   `./dev/eval-routine.sh` (it runs `./dev/eval-probe.py`, `./dev/eval-hunt.py`,
   and `./dev/eval-triggers.py` in parallel after lint). The `./dev/` scripts
   are wrappers: the tools ship in `craft/skills/skill-eval/scripts/`. Lint
   already ran the free contract checks (`./dev/eval-check.py`); probes ask the
   changed skill one cached question per high-stakes rule, the hunt measures
   what the diff made ambiguous, the trigger test re-routes requests when a
   description changed — cents, a minute or two. Agent-run cases
   (`./dev/eval-changed.sh --audit`) are a manual audit only; a blind round is a
   release audit, not the gate on a change. Before any eval work, read
   [running.md](./craft/skills/skill-eval/references/running.md) (work order,
   costs, long runs, tokens) and
   [pitfalls.md](./craft/skills/skill-eval/references/pitfalls.md) (mistakes
   past runs paid for). A `LESSONS.md` change is a behaviour change too: skills
   load it at run time.
7. **Skills stay interactive.** A skill that asks and waits is correct; never
   add an "if no user is reachable, assume X and continue" fallback. Wiring an
   unattended run belongs to the caller or an explicit mode (`auto`, `loop`).

## Dev loop

Load a group straight from the repo and reload after edits — no reinstall:

```bash
claude --plugin-dir ./srd      # repeat the flag for more groups
# …edit a SKILL.md…
/reload-plugins                       # live pick-up
/srd:questions              # test (skills are namespaced /group:skill)
```

## Active Skill Catalog

One line per skill for orientation; each skill's `SKILL.md` description is the
source of truth.

### go

- `style` — the enforced Go style rules (Production + Test): read before any
  `.go` edit, or run it on a target for a style-only check-and-fix pass.
- `review` — done-time review of finished Go code; delegates the style pass to
  `style` and adds correctness; also owns adding and learning style rules.
- `cover` — raises Go test coverage per function, measured from direct tests
  only.
- `doc` — fixes and completes in-source godoc and comments per documentable
  item; edits and verifies.
- `reshape` — proposes consumer-driven API changes to a library the project
  uses; read-only.
- `audit` — read-only audit across review, cover, doc, and reshape, merged
  into one graded findings report naming each fix command.

### srd

- `init` — sets up a folder for the srd skills: proposes the
  `project-config.md` keys it lacks, writes them after one confirmation, and
  creates their folders; the one srd skill that skips the gate.
- `create` — interviews, drafts, and self-checks a new SRD; owns the shared
  SRD references, including the `project-config.md` gate every srd skill runs
  first.
- `review` — read-only SRD review; findings go to `<srd>.review.md` beside the
  source.
- `edit` — edits an existing SRD in place, one confirmed change at a time.
- `doc-edit` — edits any other corpus page (glossary, synced doc, KB) in place,
  one confirmed change at a time; files what nobody can confirm as gaps and
  fills the gaps its edits answer.
- `questions` — build-readiness questions for an SRD; owns
  `<srd>.questions.md`. Banks platform facts through `kb`.
- `report-doc-gap` — producer side of the doc-gap loop: captures gaps found
  during SRD work as server-side drafts, files them on confirmation.
- `backlog` — one sitting over three lists: questions deferred during SRD work,
  facts nobody has pinned down, and reported gaps it fills from the corpus.
- `kb` — owns the knowledge base: writes facts attested during SRD interviews
  to its inbox, then files them into topic pages.

### craft

- `cm` — Conventional Commit messages with kernel-style bodies, from the diff
  only; `apply` splits the working tree into logical commits, `asis` commits
  it whole.
- `grill-me` — relentless planning interview until shared understanding.
- `plan-smith` — writes and tracks an implementation plan (checkbox items,
  Y/N/X status table).
- `readme-smith` — authors and audits project READMEs against its
  `references/template.md`.
- `doc-smith` — writes, audits, proofs, and collaboratively revises
  technical docs and user manuals; models the whole document to catch
  contradictions, drift, and gaps, and re-checks each edit against the rest.
- `skill-enhance` — harvests session corrections into per-skill lessons (every
  skill used, or one named), routing style rules and platform facts to the
  `learn` modes that own them; retrofits the `## Self-learning` block.
- `skill-fold-lessons` — folds `LESSONS.md` rules and pending skill edits into
  the skills, keeping only what generalizes; validates each, then tests it
  through `skill-eval run`.
- `skill-eval` — the eval suite: lint, contracts, probes, hunt, triggers,
  agent cases, token cost; `audit` (default, read-only), `run`, and `fix` (one
  committed improvement at a time). Ships the eval scripts and the authoring
  standard (`references/authoring.md`).
- `fix-all` — fixes every finding in the conversation, one commit each, after
  one up-front question round for contract and compatibility changes.

### web

- `style` — the enforced Vue 3 + TypeScript style rules (Production + Test)
  and the reference Biome config: read before any `.vue`/`.ts` edit, or run
  it on a target for a style-only check-and-fix pass.
- `review` — done-time review of finished frontend code; delegates the style
  pass to `style`, adds correctness and the `api.ts` ↔ Go JSON contract; also
  owns adding and learning style rules.
- `cover` — raises Vitest coverage per function, store, or component,
  measured from direct tests only.
- `doc` — fixes and completes module TSDoc, symbol TSDoc, component header
  blocks, and inline comments per documentable item; edits and verifies.
- `e2e` — raises Playwright coverage per route and control, proving each spec
  can fail; extends the Go fake upstream when a route needs it.
- `improve` — audits a running web app in a visible Chrome and commits one
  ranked UX fix at a time with before/after pictures; interactive by default,
  `auto` and `loop` for unattended runs. Needs the craft plugin (`craft:cm`).
- `perf` — measures a running web app in a visible Chrome at a 4x CPU
  slowdown and commits one measured speed or memory fix at a time, front end
  and live-reloading back end, never changing what the user sees; interactive
  by default, `auto` and `loop` for unattended runs. Needs the craft plugin.
- `audit` — read-only audit across review, cover, doc, and e2e, merged into
  one graded findings report naming each fix command.

### notify

Ships no skills. `hooks/hooks.json` registers `Stop` and `Notification`, both
running `hooks/notify-project.sh` via `${CLAUDE_PLUGIN_ROOT}`; that script reads
the hook JSON from stdin and hands the message and project name to
`hooks/notify-monitors.py`, which draws a GTK card on every monitor. Events
carrying `agent_id` (fired inside a subagent) are dropped. Linux
(X11/XWayland) and macOS only, degrading to `notify-send` and then to stderr.
Hooks are read at session start — test a change by restarting, not with
`/reload-plugins`.

## More Detail

- [README.md](./README.md) — overview, install, and dev loop
- [STRUCTURE.md](./STRUCTURE.md) — directory map and the plugin model
- [CONTRIBUTING.md](./CONTRIBUTING.md) — how to add, rename, and retire skills
- [ONBOARDING.md](./ONBOARDING.md) — machine setup
