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
│   └── version.sh                  # Syncs manifest versions with the VER file
├── .claude-plugin/
│   └── marketplace.json            # Marketplace catalog: the three plugins below
│
├── golang/                         # Plugin: Go workflow
│   ├── .claude-plugin/plugin.json
│   └── skills/
│       ├── style/               # Enforced Go style ruleset (prod + test)
│       ├── review/              # Done-time Go review + rule editing
│       └── cover/               # Per-function Go test coverage improvement
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
        └── skill-smith/            # Author and improve skills
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
not shipped content**, so it lives outside the repo at one fixed, tool-agnostic,
per-machine path shared by Claude and Grok:

```
${XDG_DATA_HOME:-~/.local/share}/ctx42-srd/memory.md
```

The repo ships only `memory.template.md`, used to seed the file on a fresh
machine. See that skill's `SKILL.md` for the resolution and migration rules.

---
