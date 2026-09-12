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
├── dev/                            # Maintainer scripts (no jq / external deps)
│   ├── lint-skills.sh              # Checks skills against the authoring standard
│   ├── version.sh                  # Syncs manifest versions with the VER file
│   ├── token-report.sh             # Per-skill always-loaded token surface
│   ├── check-srd-standard.sh       # Passive tripwire: source page_version vs the copy's provenance banner
│   ├── srd-subst.sh                # Deterministic vr-internal-reference swaps for the srd-sync skill
│   ├── srd-standard.header.md      # Hand-maintained frame prepended to srd-standard.md (srd-sync skill)
│   ├── srd-untranscribed-examples.md # Upstream example ids not yet transcribed into authoring-guide.md
│   └── srd-standard.footer.md      # Hand-maintained frame appended to srd-standard.md (Quality Bar)
├── .claude/
│   └── skills/srd-sync/            # Project-local maintainer skill: regenerate srd-standard.md (not shipped)
├── .claude-plugin/
│   └── marketplace.json            # Marketplace catalog: the three plugins below
│
├── golang/                         # Plugin: Go workflow
│   ├── .claude-plugin/plugin.json
│   └── skills/
│       ├── style/               # Go style ruleset + style-only pass (prod + test)
│       ├── review/              # Done-time Go review (delegates style) + rule editing
│       ├── cover/               # Per-function Go test coverage improvement
│       ├── doc/                 # Per-item godoc + comment fix and completion
│       └── reshape/             # Consumer-driven library API-change proposals
├── srd/                            # Plugin: SRD lifecycle
│   ├── .claude-plugin/plugin.json
│   └── skills/
│       ├── create/              # Author a new SRD to the SRD standard
│       ├── review/              # Read-only review of an SRD
│       ├── edit/                # Interactive in-place editing of an SRD
│       ├── system-check/        # Build-readiness review (system-knowledge)
│       ├── report-doc-gap/      # Producer: capture and file doc gaps
│       ├── backlog/             # Consumer: deferred, unknowns, and doc gaps
│       └── kb/                  # Owns the knowledge base: capture and write
└── craft/                          # Plugin: cross-cutting engineering-craft aids
    ├── .claude-plugin/plugin.json
    └── skills/
        ├── cm/                     # Conventional commit messages
        ├── grill-me/               # Planning interview
        ├── plan-smith/             # Write and track implementation plans
        ├── skill-smith/            # Author and improve skills
        ├── readme-smith/           # Author and improve project READMEs
        ├── doc-smith/              # Write, revise, audit, proof docs & manuals
        └── enhance-skills/         # Record lessons into skills; self-learning
```

Skills are grouped into **three plugins** (`golang`, `srd`, `craft`).
Each plugin is a directory with a `.claude-plugin/plugin.json` manifest and a
`skills/` folder holding one directory per skill. Each skill directory has a
`SKILL.md` (the prompt, including its `## Usage` block) and an
`evals/evals.json` (its eval scenarios). Skills ship no `README.md` — the
repo-level one orients humans.

---

## The Plugin Model

Claude consumes the skills as plugins, not as loose skill folders:

- `.claude-plugin/marketplace.json` lists the three plugins, each pointing at its
  group directory via `source` (e.g. `"./srd"`). Skills inside a group are
  discovered by the default `skills/` scan — the marketplace does not list them
  individually.
- Each group's `.claude-plugin/plugin.json` names the plugin. That name becomes
  the skill namespace: `create` is invoked as `/srd:create`.

Install and update commands are in [README.md](./README.md#install); the
edit-test dev loop (`--plugin-dir` + `/reload-plugins`) is in
[CONTRIBUTING.md](./CONTRIBUTING.md).

---

## Cross-Skill References

Skills in the same plugin are copied together into the plugin cache, so they
reference each other with relative paths from their own directory:

- `review`, `edit`, and `system-check` read `../create/references/*`.
- `backlog` reads `../kb/references/retrieval-authoring.md`, which `kb` owns.
- `cover` and `doc` read `../style/SKILL.md`; `review` invokes `golang:style`
  for the style pass and writes rule edits to `../style/SKILL.md` +
  `../style/rules.md`.

Keep these skills within the same plugin so the `../sibling` paths resolve.

---

## Per-machine data

Skills that keep user data store it outside the repo, under one fixed,
`$HOME`-rooted root so it survives plugin updates:

```
~/.agent-data/ctx42-skills/srd/kb-root            the knowledge-base directory
~/.agent-data/ctx42-skills/srd/kb/<srd-id>.json   kb capture buffer
~/.agent-data/ctx42-skills/srd/docgaps/<srd-id>.json   doc-gap buffer
~/.agent-data/ctx42-skills/lessons/<plugin>/<skill>.md self-learning lessons
```

The `srd/` segment scopes that subtree to the `srd` skills, so only they load
it. See each skill's `SKILL.md` for the resolution rules.

Old pattern: `system-check` used to keep platform knowledge in a per-machine
`memory.md` under the same root, seeded from a shipped template. That store is
retired — platform knowledge now lives in the knowledge base, which `srd:kb`
owns and the `srd-doc` corpus serves to every agent on every machine.

---
