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

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/go/review.md` (pass `~` as
is, the file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable. A missing file needs no comment. On a correction or self-caught
mistake, append a one-line rule — general, naming nothing from the project at
hand (its files, tests, tickets) — to the sibling when this directory is
writable, else to the fallback, creating it, and report where.
EOF_0
