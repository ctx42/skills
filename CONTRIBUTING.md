# Contributing to Skills

This document explains how to add, organize, and maintain skills in this
repository. Skills ship as Claude Code plugins, grouped into `golang`,
`srd`, and `craft`.

## Core Principles

- Skills grouped into plugins by purpose
- High-quality and focused skills

## Where to Place a New Skill

A skill lives at `<group>/skills/<skill-name>/`. Pick the group by purpose:

| Group    | For                                     |
| -------- | --------------------------------------- |
| `golang` | Go tooling (style, review, coverage)    |
| `srd`    | Software Requirement Document lifecycle |
| `craft`  | Cross-cutting engineering-craft aids    |

Adding a skill to an existing group needs **no** marketplace change — the
plugin's default `skills/` scan discovers it. Only a brand-new group needs its
own `.claude-plugin/plugin.json` plus an entry in
[`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json).

Keep interdependent skills in the **same** group: siblings are cached together
and reference each other as `../sibling/...`, which only resolves within a plugin.

## Naming Convention

- No org or vendor prefix.
- Use clear, lowercase, hyphenated names.
- Examples: `style`, `review`, `cm`, `grill-me`.

## Required Structure

Every skill needs its own directory containing:

- `SKILL.md` — the prompt, with proper YAML frontmatter (below)
- `README.md` — concise human usage examples and when-to-use guidance, with an
  `## Evaluations` section (≥ 3 scenarios, ≥ 1 asserting terse output)

Use **strict-portable** frontmatter — `name` + `description` only (plus the
allowed optional `license`/`version`/`tags`/`author`/`metadata`). Do **not** add
platform extensions such as `user_invocable`; they break Grok/Claude
portability. See `craft/skills/skill-smith/standards.md` for the full ruleset.

```markdown
---
name: my-skill-name
description: >
  Clear description of what the skill does and when to use it, with concrete
  trigger terms. Third person.
---
```

## Develop and Test

Load the group from the repo and reload after edits — no reinstall needed:

```bash
claude --plugin-dir ./<group>        # e.g. ./srd; repeat for more groups
# …edit a SKILL.md…
/reload-plugins                       # picks up the change live
/<group>:<skill>                      # test it (plugin skills are namespaced)
```

To test the real install experience, add the repo as a local marketplace once
(`claude plugin marketplace add ./`) and `claude plugin install <group>@ctx42-skills`;
refresh later with `claude plugin marketplace update ctx42-skills`.

## Linting

Before committing a new or changed skill, run the linter:

```bash
# from the repo root
./lint-skills.sh
```

It checks every skill against the mechanical parts of
`craft/skills/skill-smith/standards.md`: `SKILL.md` + `README.md` present,
strict-portable frontmatter (`name` + `description`, `name` equals the directory,
no forbidden keys), no dynamic injection or `$ARGUMENTS` in the body, an
`## Evaluations` section in the README, and a Contents list on any bundled
reference over ~100 lines. It also verifies each plugin `source` is a real plugin
directory and every skill sits under exactly one plugin's `skills/` dir. It edits
nothing and exits non-zero on any error.

## Documentation

When adding a skill, update:

- The skill's own `README.md`
- Top-level `README.md`
- `STRUCTURE.md` if it changes the overall map
- `AGENTS.md` skill catalog
- `ONBOARDING.md` if relevant for new users

## Renaming a Skill

1. Rename the directory (keep the `name:` frontmatter in `SKILL.md` in sync).
2. Update any `../sibling` references that pointed at the old name.
3. Run `./lint-skills.sh`, then `/reload-plugins` to pick up the change.
4. Update documentation.

## Retiring a Skill

1. Delete its directory. Its history stays in Git if you need to recover it.
2. If it was the last skill in a group, also remove the group's marketplace entry
   and directory.
3. Run `./lint-skills.sh`, then `/reload-plugins`.
4. Remove it from the documentation skill lists.
