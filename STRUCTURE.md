# Skills Directory Structure

This document describes the organization of the central skills repository.

It holds reusable skills for **Claude**. The skills ship as Claude Code plugins.

---

## Top-Level Layout

```
<repo-root>/
├── README.md
├── CONTRIBUTING.md
├── STRUCTURE.md
├── ONBOARDING.md
├── AGENTS.md                       # Guide for AI agents working in this repo
├── dev/                            # Maintainer scripts (no jq; node for case lint)
│   ├── lint-skills.sh              # Checks skills against the authoring standard
│   ├── lint-cases.mjs              # Its native-case half (node: JS regexes)
│   ├── version.sh                  # Syncs manifest versions with the VER file
│   ├── token-report.sh             # Per-skill always-loaded token surface
│   ├── eval-routine.sh             # Routine check: lint, then probes/hunt/triggers
│   ├── eval-check.py               # Free eval checks: contracts, probes, triggers
│   ├── eval-probe.py               # Batched, cached probes per skill (cents)
│   ├── eval-hunt.py                # Measures what a diff made ambiguous (cents)
│   ├── eval-triggers.py            # Routes requests against all skill descriptions
│   ├── eval-regrade.py             # Re-grades a saved agent-run trace offline
│   ├── eval-changed.sh             # Manual audit: runs the agent-run cases
│   ├── eval-ledger.py              # Its pass ledger: skips cases passed on same inputs
│   └── eval/                       # Native-case guide, prompts, triggers.json
│       └── gen/<skill>/            # Case generators: the source of a skill's cases
├── .claude/
│   └── hooks/skill-guard.sh        # Reminds an edit in a skill of the authoring conventions
├── .claude-plugin/
│   └── marketplace.json            # Marketplace catalog: the four plugins below
│
├── go/                             # Plugin: Go workflow
│   ├── .claude-plugin/plugin.json
│   ├── evals/                      # Native eval cases (<skill>--<scenario>/)
│   └── skills/
│       ├── style/               # Go style ruleset + style-only pass (prod + test)
│       ├── review/              # Done-time Go review (delegates style) + rule editing
│       ├── cover/               # Per-function Go test coverage improvement
│       ├── doc/                 # Per-item godoc + comment fix and completion
│       └── reshape/             # Consumer-driven library API-change proposals
├── srd/                            # Plugin: SRD lifecycle
│   ├── .claude-plugin/plugin.json
│   ├── evals/                      # Native eval cases (<skill>--<scenario>/), srd-doc mocks
│   │                               #   with the frozen SRD standard, fixtures/project-config.md
│   └── skills/
│       ├── create/              # Author a new SRD to the SRD standard
│       ├── review/              # Read-only review of an SRD
│       ├── edit/                # Interactive in-place editing of an SRD
│       ├── system-check/        # Build-readiness review (system-knowledge)
│       ├── report-doc-gap/      # Producer: capture and file doc gaps
│       ├── backlog/             # Consumer: deferred, unknowns, and doc gaps
│       └── kb/                  # Owns the knowledge base: capture and write
├── craft/                          # Plugin: cross-cutting engineering-craft aids
│   ├── .claude-plugin/plugin.json
│   ├── evals/                      # Native eval cases (<skill>--<scenario>/)
│   └── skills/
│       ├── cm/                     # Conventional commit messages
│       ├── grill-me/               # Planning interview
│       ├── plan-smith/             # Write and track implementation plans
│       ├── readme-smith/           # Author and improve project READMEs
│       ├── doc-smith/              # Write, revise, audit, proof docs & manuals
│       └── enhance-skills/         # Record lessons into skills; self-learning
└── notify/                         # Plugin: desktop attention hooks (no skills)
    ├── .claude-plugin/plugin.json
    └── hooks/
        ├── hooks.json              # Registers Stop + Notification
        ├── notify-project.sh       # The hook: parses hook JSON, dispatches
        └── notify-monitors.py      # GTK card drawn on every monitor
```

Skills are grouped into **three plugins** (`go`, `srd`, `craft`); a fourth,
`notify`, ships hooks instead of skills.
Each skill plugin is a directory with a `.claude-plugin/plugin.json` manifest and
a `skills/` folder holding one directory per skill. Each skill directory has a
`SKILL.md` (the prompt, including its `## Usage` block), an `evals/evals.json`
(its eval scenarios), an `evals/expectations.json` (how each is graded, kept
apart so a run can be handed a scenario without its rubric), an
`evals/contract.json` (its high-stakes rules as phrases its text must keep),
and an `evals/probes.json` (one cheap question per rule likely to regress).
Skills ship no `README.md` — the repo-level one orients humans.

---

## The Plugin Model

Claude consumes the skills as plugins, not as loose skill folders:

- `.claude-plugin/marketplace.json` lists the four plugins, each pointing at its
  group directory via `source` (e.g. `"./srd"`). Skills inside a group are
  discovered by the default `skills/` scan — the marketplace does not list them
  individually.
- Each group's `.claude-plugin/plugin.json` names the plugin. That name becomes
  the skill namespace: `create` is invoked as `/srd:create`.
- A plugin may ship no skills at all. `notify` carries only
  `hooks/hooks.json`, whose commands resolve through `${CLAUDE_PLUGIN_ROOT}`
  so they work from the plugin cache as well as from `--plugin-dir`. Hooks load
  at session start, so a change there needs a restart, not `/reload-plugins`.
  `dev/lint-skills.sh` walks only directories holding a `SKILL.md`, so a
  skill-less plugin is checked for its manifest and version alone.

Install and update commands are in [README.md](./README.md#install); the
edit-test dev loop (`--plugin-dir` + `/reload-plugins`) is in
[CONTRIBUTING.md](./CONTRIBUTING.md).

---

## Cross-Skill References

Skills in the same plugin are copied together into the plugin cache, so they
reference each other with relative paths from their own directory:

- `review`, `edit`, `system-check`, `kb`, `report-doc-gap`, and `backlog` read
  `../create/references/*`; every srd skill runs the gate in
  `../create/references/project-config.md` first.
- `backlog` reads `../kb/references/retrieval-authoring.md`, which `kb` owns.
- `cover` and `doc` read `../style/SKILL.md`; `review` invokes `go:style`
  for the style pass and writes rule edits to `../style/SKILL.md` +
  `../style/rules.md`.

Keep these skills within the same plugin so the `../sibling` paths resolve.

A path written in a `references/` file needs one more `..` than the same path
in a `SKILL.md`, since it sits a directory deeper — `../../create/references/`
from `edit/references/autofix.md`, `../create/references/` from
`edit/SKILL.md`. `dev/lint-skills.sh` resolves every relative link in both and
fails on one that points nowhere; it was added after a reference file lost its
only link to a sibling by carrying the SKILL.md spelling.

---

## Where skill data lives

The `srd` skills keep no per-machine state for project data. Everything they
need lives in the skill or in the project:

- `project-config.md` at the project root — committed; names the MCP server,
  the knowledge-base folder, the SRD folder, the SRD standard's document id,
  and the Company Glossary. Every srd skill reads it and checks the server
  before any work.
- Doc gaps — server-side, in the gap store; an unfiled gap is a `draft` there.
- Platform facts — `<kb>/_inbox.md` the moment they are confirmed, filed into
  topic pages later by `srd:kb`.
- The SRD standard and the glossary — read live through the server.

The only per-machine data is self-learning lessons, under one `$HOME`-rooted
root so they survive plugin updates:

```
~/.agent-data/ctx42-skills/lessons/<plugin>/<skill>.md
```

---
