# Contributing to Skills

This document explains how to add, organize, and maintain skills in this
repository. Skills ship as Claude Code plugins, grouped into `go`, `srd`,
and `craft`.

## Core Principles

- Skills grouped into plugins by purpose
- High-quality and focused skills

## Where to Place a New Skill

A skill lives at `<group>/skills/<skill-name>/`. Pick the group by purpose:

| Group   | For                                     |
|---------|-----------------------------------------|
| `go`    | Go tooling (style, review, coverage)    |
| `srd`   | Software Requirement Document lifecycle |
| `craft` | Cross-cutting engineering-craft aids    |

The fourth plugin, `notify`, is hooks-only and holds no `skills/` directory —
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

Every skill needs its own directory containing:

- `SKILL.md` — the prompt, with proper YAML frontmatter (below) and a
  `## Usage` block right after the H1 title
- `evals/evals.json` — the skill's eval scenarios (≥ 3), in the shape
  `{id, name, skills, setup, query, files}`. `setup` is the state the run
  starts from; without it most expectations cannot be graded, and several were
  found to pass no matter what the skill did.
- `evals/expectations.json` — the pass criteria, `{id, name,
  expected_behavior[]}`, one entry per scenario id, ≥ 1 asserting terse output.

Run them with two agents, never one: a runner that sees `evals.json` and never
`expectations.json`, then a grader that sees `expectations.json` and never
`SKILL.md`. Ask the runner what in the instructions was ambiguous or had to be
guessed at — in the first full round that question found more defects than the
pass counts did — but its answer is a backlog, not a work list (see *The eval
loop* below).

A scenario may add `requires` when it cannot run on an ordinary checkout — a
private mirror, a live service, a toolchain. Say what is needed and what a
stand-in does and does not establish, so a run that cannot meet it reports the
scenario blocked instead of quietly narrating one.

**Two files, deliberately.** A run must be able to read a scenario without the
rubric it will be graded on. While both lived in one file, no eval in this repo
was blind — every agent that ran one said so unprompted, and a scenario whose
expectations you have already read measures whether the instructions are
followable, not whether an uninformed agent follows them. The linter checks the
ids match and that no `expected_behavior` leaks back into `evals.json`.

The two prompts are `dev/eval/blind-runner-prompt.md` and
`dev/eval/grader-prompt.md`, kept outside `tmp/` so reading one does not break
the runner's own don't-read-`tmp/` rule. Hand them over verbatim once
`<REPO>` and `<HOME>` are replaced with the repo root and your home directory.

**What to distrust in a result.**

- *One agent doing both jobs.* Its pass counts mean "these instructions are
  followable", not "an uninformed agent follows them".
- *`"files": []`.* The runner then authors the corpus it is graded on. A real
  fixture under `assets/` is stronger; `srd:review`'s `flawed-srd.md` is the
  model. Its scenario's bullets are the baseline of every defect it plants:
  plant one only with its bullet, and add any defect a run finds that no
  bullet lists. A fixture never names its expectations file — a blind runner
  reads it.
- *An interview skill.* `grill-me`, `srd:create`, `srd:edit` need someone to
  play the user, and one agent playing both sides is a weak test. Have it
  write the persona's ground truth down first and say where it was generous.
- *A pre-fix run graded against post-fix expectations.* Editing a scenario or
  an expectation after a run invalidates that run's verdict on it. Re-run, or
  tell the grader which bullets the edit reaches.

**Make every count re-derivable, and say so in the skill.** Four skills shipped
a wrong number to the user this round — a backoff delay the code never sleeps,
"~300 characters" over an example that renders 185, a fan-out total of 48 where
the workers summed to 45, "12 terms digested" from a glossary defining 10. Each
was true when it was written and wrong by the time it shipped, and none of the
four runs noticed. A skill that reports a count needs a line telling it to read
that count off the finished artifact rather than carry it from the work, and a
scenario that grades the count against the file. It is the one number nobody
re-derives, which is exactly why it is worth grading.

**Three tiers.** A skill change is confirmed in minutes, not in a round:

1. *Lint* (`./dev/lint-skills.sh`, seconds). A wording or clarification edit
   stops here, after a re-read.
2. *Native cases* (`./dev/eval-changed.sh`, a few minutes). A behaviour change
   runs the cases its diff reaches: each one invokes the real skill through
   `claude plugin eval`, on a scripted fixture with mocked MCP servers, graded
   mostly by deterministic checks. Authoring rules: `dev/eval/native-cases.md`.
   A scenario edited in `evals.json` or `expectations.json` gets its case
   updated in the same change. Run it without asking; it costs cents per case.
3. *Blind round* (the runner and grader prompts above). An audit before a
   release or after a large refactor, never the gate on an ordinary change.

**The eval loop.** A blind round costs hundreds of thousands of tokens, and a
runner always finds something new to doubt, so the loop ends only on these
rules:

- Edit a skill only for a graded FAIL, a disagreement measured on identical
  input (workers or runs splitting on the same bytes), or a miss on real code
  the user reports. Anything else — a runner's ambiguity list included — goes
  to `tmp/eval-backlog.md` and triggers no re-run.
- Before any blind round, state its scope and rough cost and get the user's
  go-ahead.
- A behaviour change re-runs only the scenarios it reaches, never the suite.
- One fix-and-re-run per FAIL; a bullet that fails again after its fix goes to
  the user as a design question, not another rewording.
- At most two rounds per change unless the user raises it; a round with every
  gradable bullet PASS and no measured split ends the loop — no confirmation
  round, no new scenario for a guard that has never fired.
- Freeze `expectations.json` while a loop runs: batch the defects a grader
  finds and apply them after it ends, so no round grades a moved target.

Without these rules, three consecutive `go:style` rounds passed every bullet,
yet cost about a million tokens, because each runner's new ambiguity list was
treated as the next round's work and nothing measured what those edits bought.

**Live services and real stores.** The `srd-doc` server is production — the
INFRAPORT corpus and a gap store whose drafts are real records — and
`$HOME/.agent-data/` holds the user's real lesson files. Tell every agent so
explicitly: the server's read tools are the only safe calls, and every
`$HOME/.agent-data` path a skill resolves must be redirected into the run's
workspace. Both have been violated by eval agents following the skills
faithfully — once filing a probe record that needed a hand edit to remove,
once by a skill that reached a store only through another skill.

**The SRD standard in evals.** At run time the srd skills read the standard
live through the server (`get_doc` on the `srd-standard` id in the project's
`project-config.md`); no copy ships. Evals grade against a fixed one instead:
`srd/evals/mocks/srd-doc/fixtures/srd-standard.md`, test data only, which the
native cases' `get_doc` mock serves, with `srd/evals/fixtures/project-config.md`
for the gate. `dev/eval/blind-runner-prompt.md` tells the runner to substitute
both. Cases that override `get_doc` carry copies of the standard, which
`dev/lint-skills.sh` keeps identical to it. Change the frozen standard only
together with the scenarios graded on it.

Skills ship no `README.md`. Everything a user or agent needs lives in
`SKILL.md`, its bundled files, and `evals/evals.json`; the repo-level
`README.md` is where humans get oriented. A skill README is a second copy of
what `SKILL.md` already says, kept in step by nothing — `dev/lint-skills.sh`
fails on one.

Frontmatter requires `name` + `description`; optional metadata (`license`/
`version`/`tags`/`author`/`metadata`) is allowed but used sparingly.
Claude-native affordances are permitted and encouraged where they earn their
place: `argument-hint`, `$ARGUMENTS` body substitution, and dynamic injection
(`` !`cmd` ``). Beyond that, follow Anthropic's Agent Skills authoring
guidance; `dev/lint-skills.sh` enforces the mechanical parts.

### Argument substitution, measured

Verified against `claude -p` on 2026-09-12, because the behaviour is
undocumented and two parts of it are surprising:

| Written        | With `/skill ONE TWO THREE` | With no arguments |
|----------------|-----------------------------|-------------------|
| `$ARGUMENTS`   | `ONE TWO THREE`             | empty string      |
| `$0`           | `ONE`                       | left literal      |
| `$1`           | `TWO`                       | left literal      |
| `$9`           | left literal (out of range) | left literal      |

Two consequences, both of which bit this repo:

- **Positional arguments are zero-indexed.** `$0` is the first argument, not
  the skill name. Every skill here that read `$1` as "the first token" was
  reading the second, silently taking the wrong word as its mode.
- **Substitution ignores backticks and fenced code blocks.** There is no
  escape. Prose that *explains* the convention is destroyed by it: a line
  reading ``` `$1` is the SRD path ``` arrives as ``` `TWO` is the SRD path ```.

So: use `$ARGUMENTS` where the value should be inlined, and describe positions
in words ("the first token", "the tokens after it"). Do not write `$N` in a
skill body, and do not write about `$ARGUMENTS` in prose that must survive
substitution — say "with no arguments", not "with no `$ARGUMENTS`".

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

It checks the mechanical parts of the skill layout: `SKILL.md` present with a
`## Usage` block, frontmatter carries `name` + `description` with `name` equal
to the directory, the body carries the output-discipline line, `evals/evals.json`
holds at least 3 scenarios, no `README.md` sits in the skill directory, and any
bundled reference over ~100 lines starts with a Contents list. It also
verifies each plugin `source` is a real plugin directory and every skill sits
under exactly one plugin's `skills/` dir. It edits nothing and exits non-zero on
any error.

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
