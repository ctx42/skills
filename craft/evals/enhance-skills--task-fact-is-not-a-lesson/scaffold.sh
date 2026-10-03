#!/usr/bin/env bash
set -euo pipefail
mkdir -p craft/skills/doc-smith
cat > craft/skills/doc-smith/SKILL.md <<'EOF_0'
---
name: doc-smith
description: >
  Writes and reviews technical documentation.
license: MIT
---

# doc-smith

Writes and reviews technical documentation and user manuals.

## Steps

1. Read the sources the user names.
2. Draft or review the document section by section.
3. Write the result where the user asks.

## Output

Name the file written and the sections touched.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/craft/doc-smith.md`,
the sibling winning a conflict — a read-only install writes the second, and what
it learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule to the sibling when this directory
is writable, else to the fallback, creating it, and report where.
EOF_0
