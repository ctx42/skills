# Skills Directory Structure

This document describes the organization of the central skills repository.

It holds reusable skills used by both **Grok** and **Claude**. The skills ship
as Claude Code plugins.

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
│   └── srd-standard.footer.md      # Hand-maintained frame appended to srd-standard.md (Quality Bar)
├── .claude/
│   └── skills/srd-sync/            # Project-local maintainer skill: regenerate srd-standard.md (not shipped)
├── .claude-plugin/
│   └── marketplace.json            # Marketplace catalog: the three plugins below
│
├── golang/                         # Plugin: Go workflow
│   ├── .claude-plugin/plugin.json
│   └── skills/
│       ├── style/               # Enforced Go style ruleset (prod + test)
│       ├── review/              # Done-time Go review + rule editing
│       ├── cover/               # Per-function Go test coverage improvement
│       └── reshape/             # Consumer-driven library API-change proposals
├── srd/                            # Plugin: SRD lifecycle
│   ├── .claude-plugin/plugin.json
│   └── skills/
│       ├── create/             # Author a new SRD to the SRD standard
│       ├── review/             # Read-only review of an SRD
│       ├── edit/               # Interactive in-place editing of an SRD
│       └── system-check/       # Build-readiness review (system-knowledge)
└── craft/                          # Plugin: cross-cutting engineering-craft aids
    ├── .claude-plugin/plugin.json
    └── skills/
        ├── cm/                     # Conventional commit messages
        ├── grill-me/               # Planning interview
        ├── plan-smith/             # Write and track implementation plans
        ├── skill-smith/            # Author and improve skills
        ├── readme-smith/           # Author and improve project READMEs
        ├── doc-smith/              # Write, revise, audit, proofread docs & manuals
        └── enhance-skills/         # Record lessons into skills; self-learning
```

Skills are grouped into **three plugins** (`golang`, `srd`, `craft`).
Each plugin is a directory with a `.claude-plugin/plugin.json` manifest and a
`skills/` folder holding one directory per skill. Each skill directory has a
`SKILL.md` (the prompt) and a `README.md` (human usage guide).

---

## The Plugin Model

Both Claude and Grok consume the skills as plugins, not as loose skill folders:

- `.claude-plugin/marketplace.json` lists the three plugins, each pointing at its
  group directory via `source` (e.g. `"./srd"`). Skills inside a group are
  discovered by the default `skills/` scan — the marketplace does not list them
  individually.
- Each group's `.claude-plugin/plugin.json` names the plugin. That name becomes
  the skill namespace: `create` is invoked as `/srd:create`.
- Grok reads Claude marketplaces and plugins directly, so the same catalog serves
  both tools with no separate wiring.

Install and update commands are in [README.md](./README.md#install); the
edit-test dev loop (`--plugin-dir` + `/reload-plugins`) is in
[CONTRIBUTING.md](./CONTRIBUTING.md).

---

## Cross-Skill References

Skills in the same plugin are copied together into the plugin cache, so they
reference each other with relative paths from their own directory:

- `review`, `edit`, and `system-check` read `../create/references/*`.
- `review` and `cover` read `../style/SKILL.md`.

Keep these skills within the same plugin so the `../sibling` paths resolve.

---

## system-check Memory

`system-check` keeps a curated platform-knowledge base. It is **user data,
not shipped content**, so it lives outside the repo at one fixed, `$HOME`-rooted,
per-machine path shared by Claude and Grok:

```
~/.agent-data/ctx42-skills/srd/memory.md
```

The `srd/` segment scopes it to the `srd` skills, so only they load it. The
`craft:enhance-skills` self-learning mechanism uses the same root:
`~/.agent-data/ctx42-skills/lessons/<plugin>/<skill>.md` for skills that run
from a read-only install. The repo ships only `memory.template.md`, used to seed
`memory.md` on a fresh machine; older installs migrate per
`srd/skills/system-check/references/memory-migration.md`. See each skill's
`SKILL.md` for the resolution rules.

---
