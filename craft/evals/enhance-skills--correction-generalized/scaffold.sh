#!/usr/bin/env bash
set -euo pipefail
mkdir -p go/skills/review
cat > go/skills/review/SKILL.md <<'EOF_0'
---
name: review
description: >
  Done-time Go quality review.
license: MIT
---

# review

Done-time Go quality review of a diff, a package, or a module.

## Steps

1. Read the target files.
2. Check each against the style rules and for correctness: bugs, edge cases,
   error handling.
3. Report findings grouped as Bugs, then Style, each with `file:line`.

## Output

One line per finding; no preamble.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/go/review.md`,
the sibling winning a conflict — a read-only install writes the second, and what
it learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule — general, naming nothing from
the project at hand (its files, tests, tickets) — to the sibling when this
directory is writable, else to the fallback, creating it, and report where.
EOF_0
