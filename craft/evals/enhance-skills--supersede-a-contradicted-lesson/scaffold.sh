#!/usr/bin/env bash
set -euo pipefail
mkdir -p craft/skills/plan-smith
cat > craft/skills/plan-smith/SKILL.md <<'EOF_0'
---
name: plan-smith
description: >
  Writes implementation plans.
license: MIT
---

# plan-smith

Writes an implementation plan as numbered checkbox items with a status
summary table.

## Steps

1. Read the brief.
2. Write the plan as numbered checkbox items, then the status table.
3. Save the plan and name its path.

## Output

The path written and the item count.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/craft/plan-smith.md`,
the sibling winning a conflict — a read-only install writes the second, and what
it learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule to the sibling when this directory
is writable, else to the fallback, creating it, and report where.
EOF_0
mkdir -p craft/skills/plan-smith
cat > craft/skills/plan-smith/LESSONS.md <<'EOF_1'
# Lessons

Rules learned for the `plan-smith` skill. Read before running; obey each line.

- Number items continuously across sections; never restart at 1.
- Default the plan path to tmp/<slug>-plan.md without asking.
EOF_1
