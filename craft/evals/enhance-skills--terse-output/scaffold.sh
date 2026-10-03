#!/usr/bin/env bash
set -euo pipefail
mkdir -p go/skills/style
cat > go/skills/style/SKILL.md <<'EOF_0'
---
name: style
description: >
  Enforced Go coding style.
license: MIT
---

# style

Enforced Go coding style; the rulebook to read before writing Go and a
style-only pass that lists offenses across a target and proposes fixes.

## Steps

1. List the `.go` files in the target.
2. Check each against the rules below and report every offense with
   `file:line`.
3. Apply the fixes the user accepts.

## Rules

- Receivers are a short type abbreviation, never a single letter.
- Wrap errors with `%w` and add context.
- Name the actual value `have` and the expected value `want` in tests.

## Output

One line per offense; no preamble.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/go/style.md`,
the sibling winning a conflict — a read-only install writes the second, and what
it learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule to the sibling when this directory
is writable, else to the fallback, creating it, and report where.
EOF_0
mkdir -p craft/skills/cm
cat > craft/skills/cm/SKILL.md <<'EOF_1'
---
name: cm
description: >
  Writes git commit messages (Conventional Commits).
license: MIT
---

# cm

Writes a git commit message for the staged change using Conventional
Commits with a Linux kernel-style body.

## Steps

1. Read the staged diff (`git diff --cached`).
2. Write the summary line, then the body.
3. Show the message; commit only when asked.

## Summary line

- Type: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `style`, `build`,
  `ci`, `chore`, `revert`
- Scope: optional, short noun
- Description: imperative, lowercase, no period, ideally ≤ 50 chars (hard 72)

## Body

- Wrap at 72 columns.
- Imperative mood.
- Explain why the change was made; the diff shows what.

## Output

Print the message in one fenced block and nothing else.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/craft/cm.md`,
the sibling winning a conflict — a read-only install writes the second, and what
it learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule to the sibling when this directory
is writable, else to the fallback, creating it, and report where.
EOF_1
