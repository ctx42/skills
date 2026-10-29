# Contributing to Skills

This document explains how to add, organize, and maintain skills in this
repository. Skills ship as Claude Code plugins, grouped into `go`, `srd`,
`craft`, and `web`.

## Core Principles

- Skills grouped into plugins by purpose
- High-quality and focused skills

## Where to Place a New Skill

A skill lives at `<group>/skills/<skill-name>/`. Pick the group by purpose:

| Group   | For                                              |
|---------|--------------------------------------------------|
| `go`    | Go tooling (style, review, coverage)             |
| `srd`   | Software Requirement Document lifecycle          |
| `craft` | Cross-cutting engineering-craft aids             |
| `web`   | Vue/TS frontend: style, review, tests, UX, speed |

The fifth plugin, `notify`, is hooks-only and holds no `skills/` directory —
never place a skill there.

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

Every skill directory holds `SKILL.md` (frontmatter, then a `## Usage` block
right after the H1 title), `evals/evals.json` (≥ 3 scenarios),
`evals/expectations.json`, `evals/contract.json`, and `evals/probes.json`. The
full standard — structure, frontmatter, token budget, re-derivable counts, and
argument conventions — ships with the tool that enforces it, `craft:skill-eval`:
[authoring.md](./craft/skills/skill-eval/references/authoring.md).

## Testing a Change

Run `/craft:skill-eval` (a read-only audit), `/craft:skill-eval run`, or
`/craft:skill-eval fix`. The scripts behind it live in
[`craft/skills/skill-eval/scripts/`](./craft/skills/skill-eval/scripts/); the
`./dev/` wrappers run them on this repo (`./dev/lint-skills.sh`,
`./dev/eval-routine.sh`, `./dev/eval-probe.py`, …). Before eval work read
[running.md](./craft/skills/skill-eval/references/running.md) (work order,
costs, long runs) and
[pitfalls.md](./craft/skills/skill-eval/references/pitfalls.md) (mistakes past
runs paid for). The tiers and the eval loop are in
[tiers.md](./craft/skills/skill-eval/references/tiers.md); the agent-case format
in [native-cases.md](./craft/skills/skill-eval/references/native-cases.md).

What stays here is this repo's own eval material:

The blind round's two prompts are `dev/eval/blind-runner-prompt.md` and
`dev/eval/grader-prompt.md`, kept outside `tmp/` so reading one does not break
the runner's own don't-read-`tmp/` rule. Hand them over verbatim once `<REPO>`
and `<HOME>` are replaced with the repo root and your home directory.

**Live services and real stores.** The `srd` server is production — the
real documentation corpus and a gap store whose drafts are real records —
and `$HOME/.agent-data/` holds the user's real lesson files. Tell every agent so
explicitly: the server's read tools are the only safe calls, and every
`$HOME/.agent-data` path a skill resolves must be redirected into the run's
workspace. Both have been violated by eval agents following the skills
faithfully — once filing a probe record that needed a hand edit to remove,
once by a skill that reached a store only through another skill.

**The SRD standard in evals.** At run time the srd skills read the standard
live through the server (`get_doc` on the `srd-standard` id in the project's
`project-config.md`); no copy ships. Evals grade against a fixed one instead:
`srd/evals/mocks/srd/fixtures/srd-standard.md`, test data only, which the
native cases' `get_doc` mock serves, with `srd/evals/fixtures/project-config.md`
for the gate. `dev/eval/blind-runner-prompt.md` tells the runner to substitute
both. Cases that override `get_doc` carry copies of the standard, which
`dev/lint-skills.sh` keeps identical to it. Change the frozen standard only
together with the scenarios graded on it.

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

It checks the mechanical parts of the standard
([authoring.md](./craft/skills/skill-eval/references/authoring.md#mechanical-checks)),
the marketplace wiring, and the manifest versions. It edits nothing and exits
non-zero on any error.

## Folding Lessons

A skill's `LESSONS.md` is a holding area. Every so often, fold its rules into
the skill so they become part of the skill itself: run
`/craft:skill-fold-lessons`, which owns the procedure — the genericity gate,
placement, budget, guards, and tests.

## Documentation

When adding a skill, update:

- The skill's own `SKILL.md` (`## Usage`) and `evals/evals.json`
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
