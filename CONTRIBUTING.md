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
./dev/lint-skills.sh
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

`srd/skills/create/references/srd-standard.md` is **derived** from a
Confluence page (id `1949564932`, mirrored by cfsync into the private `vr`
checkout) and trimmed for agent use — never edit rule text only in the repo.
Every deliberate difference is recorded in `dev/srd-standard-sync.tsv`;
`dev/sync-srd-standard.sh verify` proves the two stay in sync and
`lint-skills.sh` runs it as a warning on machines that have the source
(elsewhere it skips). Override the source path with `SRD_STANDARD_SRC`.

**Source changed** (someone edited the Confluence page):

1. `cfsync pull` the mirror, then `./dev/sync-srd-standard.sh diff`.
2. Apply the per-unit diffs to the repo copy, keeping the trims — the
   transform spec is in the script header.
3. Refresh changed ledger hashes (`./dev/sync-srd-standard.sh hash '<unit>'`)
   and bump the `page_version` in the copy's provenance header.
4. A `page_version` bump can also mean an edit inside a **frozen node** — the
   Bad→Good example expands and the Quality Bar list render only as
   `<!-- adf:… -->` placeholders, so their content is invisible locally. Open
   the page, re-check them, and update `authoring-guide.md` / the transcribed
   Quality Bar by hand.
5. Run `./dev/sync-srd-standard.sh verify` and `./dev/lint-skills.sh`, and
   re-check the srd:review fixture eval
   (`srd/skills/review/assets/flawed-srd.md`) — its finding set must not
   shrink.

**Rule change conceived here**: edit the local mirror, `cfsync push`, then
follow the source-changed flow. Until pushed, record the rule as
`RULE:<id>	-	<sha>` (repo-only) in the ledger — `REQ-8` is the standing
example.

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
