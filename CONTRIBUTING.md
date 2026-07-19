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
|----------|-----------------------------------------|
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

Frontmatter requires `name` + `description`; optional metadata (`license`/
`version`/`tags`/`author`/`metadata`) is allowed but used sparingly.
Claude-native affordances are permitted and encouraged where they earn their
place: `argument-hint`, `$ARGUMENTS`/`$N` body substitution, and dynamic
injection (`` !`cmd` ``). See `craft/skills/skill-smith/standards.md` for the
full ruleset — this file does not duplicate it.

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
./dev/lint-skills.sh
```

It checks every skill against the mechanical parts of
`craft/skills/skill-smith/standards.md`: `SKILL.md` + `README.md` present,
frontmatter carries `name` + `description` with `name` equal to the directory,
the body carries the output-discipline line, an `## Evaluations` section in the
README, and a Contents list on any bundled reference over ~100 lines. It also
verifies each plugin `source` is a real plugin directory and every skill sits
under exactly one plugin's `skills/` dir. It edits nothing and exits non-zero on
any error.

## Documentation

When adding a skill, update:

- The skill's own `README.md`
- Top-level `README.md`
- `STRUCTURE.md` if it changes the overall map
- `AGENTS.md` skill catalog
- `ONBOARDING.md` if relevant for new users

## Versioning

The whole repo ships as one version. The **single source of truth is the `VER`
file**. Every `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
carries the same number and is **derived from `VER`, never edited by hand** — a
stale manifest version silently blocks `claude plugin update`.

**One-time per clone** — point git at the tracked hooks so the sync runs:

```shell
./dev/version.sh install-hooks   # git config core.hooksPath .githooks
```

**Releasing** — bump the version however your release process does it: update
`VER` (and `CHANGELOG.md`), commit, tag, push. The only rule is that the version
change lands as a commit that includes `VER`. On that commit the
`.githooks/pre-commit` hook fires, derives every manifest version from the
just-written `VER` (`dev/version.sh sync`), and stages the manifests — so the bump
commit, and the tag placed on it, carry matching versions. You set the version
in one place (`VER`); the manifests follow mechanically.

The manual equivalent, if you bump by hand:

```shell
printf 'v0.2.0' > VER            # set the new version
# …update CHANGELOG.md…
git add VER CHANGELOG.md         # the hook syncs + stages the manifests on commit
git commit -m 'Bump version to 0.2.0.'
git tag -a v0.2.0 -m 'Tag version v0.2.0.' && git push --follow-tags
```

Supporting commands (you rarely run these directly):

```shell
./dev/version.sh verify   # fail if any manifest disagrees with VER (run by lint-skills.sh)
./dev/version.sh sync     # write VER's number into every manifest (repairs drift)
```

`./dev/lint-skills.sh` calls `dev/version.sh verify`, so a drifted manifest also
fails the lint gate as a backstop. The hook fails closed: if a manifest cannot be
written, the commit aborts rather than releasing drift.

## Syncing the SRD standard

`srd/skills/create/references/srd-standard.md` is a **generated artifact** —
never edit it by hand. It is assembled from a Confluence page (id `1949564932`,
mirrored by cfsync into the private `vr` checkout), trimmed for agent use, and
two hand-maintained frame files in `dev/`:

```
srd-standard.md = dev/srd-standard.header.md + transform(source) + dev/srd-standard.footer.md
```

There is **no reword layer**: the copy mirrors the source text exactly, minus
the trims, so any editorial change must be made in Confluence. Override the
source path with `SRD_STANDARD_SRC`.

Regeneration is the **`srd-sync` skill** (`.claude/skills/srd-sync/`) — an
LLM-driven task, not a script, because it runs rarely and with a human in the
loop; its `SKILL.md` owns the transform, the diff buckets, and the checks. Two
scripts support it: `dev/srd-subst.sh` applies the deterministic
vr-internal-reference swaps so an LLM never edits rule text, and
`dev/check-srd-standard.sh` is the passive tripwire — it compares the source
`page_version` to the version in the copy's provenance banner, and
`lint-skills.sh` runs it as a warning where the source exists (elsewhere it
SKIPs and passes).

**Source changed** (someone edited the Confluence page):

1. `cfsync pull` the mirror.
2. Review the **frozen nodes** first — the Bad→Good example expands and the
   Quality Bar list are not in the export, so a `page_version` bump can hide an
   edit inside them. Open the page, re-check them, and update
   `srd/skills/create/references/authoring-guide.md` and
   `dev/srd-standard.footer.md` (the transcribed Quality Bar) by hand.
3. Invoke the `srd-sync` skill and review its reported diffs. LOCAL-ONLY and
   TEXT DIFFERS units are debt — push them upstream to Confluence and re-sync,
   or accept losing them (a write adopts the source wording). If the source
   grew a new top-level section, the skill hard-stops until the transform is
   extended.
4. After the skill writes, run `./dev/lint-skills.sh` and re-check the
   srd:review fixture eval (`srd/skills/review/assets/flawed-srd.md`) — its
   finding set must not shrink.

**Rule change conceived here**: a rule added to the local mirror is part of the
sync source — it surfaces as SOURCE-ONLY and a write bakes it in. Never run
srd-sync with unpushed mirror edits: add the rule to the mirror, `cfsync push`,
`cfsync pull` (confirms the page took it and bumps `page_version`), then run the
source-changed flow above. If you must sync first, `cfsync pull` to clobber the
local edit.

## Renaming a Skill

1. Rename the directory (keep the `name:` frontmatter in `SKILL.md` in sync).
2. Update any `../sibling` references that pointed at the old name.
3. Run `./dev/lint-skills.sh`, then `/reload-plugins` to pick up the change.
4. Update documentation.

## Retiring a Skill

1. Delete its directory. Its history stays in Git if you need to recover it.
2. If it was the last skill in a group, also remove the group's marketplace entry
   and directory.
3. Run `./dev/lint-skills.sh`, then `/reload-plugins`.
4. Remove it from the documentation skill lists.
