# Skill authoring standard

The standard every skill in a `<group>/skills/<name>/` repo meets.
`scripts/lint-skills.sh` checks its mechanical parts; the rest is read.

## Contents

- [Structure](#structure)
- [Token budget](#token-budget)
- [Counts](#counts)
- [Argument substitution, measured](#argument-substitution-measured)
- [Arguments](#arguments)
- [Mechanical checks](#mechanical-checks)

## Structure

Every skill needs its own directory containing:

- `SKILL.md` — the prompt, with proper YAML frontmatter (below) and a
  `## Usage` block right after the H1 title
- `evals/evals.json` — the skill's eval scenarios (≥ 3), in the shape
  `{id, name, skills, setup, query, files}`. `setup` is the state the run
  starts from; without it most expectations cannot be graded, and several were
  found to pass no matter what the skill did.
- `evals/expectations.json` — the pass criteria, `{id, name,
  expected_behavior[]}`, one entry per scenario id, ≥ 1 asserting terse output.

A scenario may add `requires` when it cannot run on an ordinary checkout — a
private mirror, a live service, a toolchain. Say what is needed and what a
stand-in does and does not establish, so a run that cannot meet it reports the
scenario blocked instead of quietly narrating one. Such a scenario needs no
native case — a case's sandbox cannot meet it either — so each of its bullets
is a probe's or `blind_only`.

**Two files, deliberately.** A run must be able to read a scenario without the
rubric it will be graded on. While both lived in one file, no eval in the
suite's home repo was blind — every agent that ran one said so unprompted, and a
scenario whose expectations you have already read measures whether the
instructions are followable, not whether an uninformed agent follows them. The
linter checks the ids match and that no `expected_behavior` leaks back into
`evals.json`.

Skills ship no `README.md`. Everything a user or agent needs lives in
`SKILL.md`, its bundled files, and `evals/evals.json`; the repo-level
`README.md` is where humans get oriented. A skill README is a second copy of
what `SKILL.md` already says, kept in step by nothing — `scripts/lint-skills.sh`
fails on one.

Frontmatter requires `name` + `description`; optional metadata (`license`/
`version`/`tags`/`author`/`metadata`) is allowed but used sparingly.
Claude-native affordances are permitted and encouraged where they earn their
place: `argument-hint`, `$ARGUMENTS` body substitution, and dynamic injection
(`` !`cmd` ``). Beyond that, follow Anthropic's Agent Skills authoring
guidance; `scripts/lint-skills.sh` enforces the mechanical parts.

## Token budget

The description and the `SKILL.md` body are paid on every session and every
trigger. Aim the description at ~350 characters (past 500 warns), the body at
~500 lines and ~5000 tokens. Prefer short, dense, imperative wording over
prose. When an edit pushes a body past the aim, move a section whose trigger is
a condition (a mode, a claim type) into `references/<name>.md` and leave a
pointer plus its one-line rule; never cut settled rules to make room. A
reference over ~100 lines starts with a Contents list.

## Counts

**Make every count re-derivable, and say so in the skill.** Four skills shipped
a wrong number to the user this round — a backoff delay the code never sleeps,
"~300 characters" over an example that renders 185, a fan-out total of 48 where
the workers summed to 45, "12 terms digested" from a glossary defining 10. Each
was true when it was written and wrong by the time it shipped, and none of the
four runs noticed. A skill that reports a count needs a line telling it to read
that count off the finished artifact rather than carry it from the work, and a
scenario that grades the count against the file. It is the one number nobody
re-derives, which is exactly why it is worth grading.

## Argument substitution, measured

Verified against `claude -p` on 2026-09-12, because the behaviour is
undocumented and two parts of it are surprising:

| Written        | With `/skill ONE TWO THREE` | With no arguments |
|----------------|-----------------------------|-------------------|
| `$ARGUMENTS`   | `ONE TWO THREE`             | empty string      |
| \$0            | `ONE`                       | left literal      |
| \$1            | `TWO`                       | left literal      |
| \$9            | left literal (out of range) | left literal      |

Two consequences, both of which bit the suite's home repo:

- **Positional arguments are zero-indexed.** \$0 is the first argument, not
  the skill name. Every skill there that read \$1 as "the first token" was
  reading the second, silently taking the wrong word as its mode.
- **Substitution ignores backticks and fenced code blocks.** There is no
  escape. Prose that *explains* the convention is destroyed by it: a line
  reading "\$1 is the SRD path" arrives as "TWO is the SRD path".

So: use `$ARGUMENTS` where the value should be inlined, and describe positions
in words ("the first token", "the tokens after it"). Do not write `$N` in a
skill body, and do not write about `$ARGUMENTS` in prose that must survive
substitution — say "with no arguments", not "with no `$ARGUMENTS`".

## Arguments

One idea has one spelling in every skill; no old spelling lives on as an
alias.

- Order: reserved words (modes, flags) and `key=value` controls go anywhere;
  anything else is the target — so is a unit selector (`func=`, `component=`,
  `route=`, `flow=`). Positional tails (an SRD path, then a line or an id) keep
  their documented order.
- Free text a skill takes (a rule, a brief, a focus, a description) runs to the
  end of the input; a reserved word inside it is text.
- Flags are bare words, never `--flag`; values are `key=value`, never
  `key value`; lists are `a,b` without spaces; finding numbers carry `#`
  (`#4,6`).
- Unknown input, verbatim in every skill that takes modes or controls: "A
  `key=value` that names no control here, or a word left over once the modes,
  the target, and any text the skill takes are read: say it was not
  recognized, name the ones that exist, and run with the defaults as if it
  were absent — unless dropping it would widen what the run changes; then ask.
  A target that resolves to nothing: say so and ask — never guess what to work
  on."
- `argument-hint` marks the default with `*`; the first Usage line is the
  default.

Shared spellings: `max=N` caps one run, in the skill's own unit; `all` is the
whole project; no target in a code skill is the working diff; `packages=`
(go) and `dirs=` (web) restrict scope; `depth=light|standard|full`;
`plan_first` proposes the budget and stops; `fix` applies findings; `only=`
filters kinds; `func=`/`component=`/`route=`/`flow=` and `FILE:LINE` name one
unit; `create`, `audit`, `walk`, `learn` are the mode words for new, check,
work-through-together, and mine-the-session. Fan-out is decided by size,
never by a flag. `scripts/lint-skills.sh` checks the mechanical parts.

```markdown
---
name: my-skill-name
description: >
  Clear description of what the skill does and when to use it, with concrete
  trigger terms. Third person.
---
```

## Mechanical checks
 `scripts/lint-skills.sh` checks the mechanical parts of the skill layout:
`SKILL.md` present with a `## Usage` block, frontmatter carries `name` +
`description` with `name` equal to the directory, the body carries the
output-discipline line, `evals/evals.json` holds at least 3 scenarios, no
`README.md` sits in the skill directory, and any bundled reference over ~100
lines starts with a Contents list. It also verifies each plugin `source` is a
real plugin directory and every skill sits under exactly one plugin's `skills/`
dir. It edits nothing and exits non-zero on any error.
