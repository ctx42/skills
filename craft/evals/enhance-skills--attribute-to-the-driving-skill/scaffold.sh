#!/usr/bin/env bash
set -euo pipefail
mkdir -p craft/skills/cm
cat > craft/skills/cm/SKILL.md <<'EOF_0'
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
EOF_0
mkdir -p srd/skills/create
cat > srd/skills/create/SKILL.md <<'EOF_1'
---
name: create
description: >
  Authors a new SRD to the SRD standard.
license: MIT
---

# create

Authors a new Software Requirement Document (SRD) to the SRD standard.

## Steps

1. Load the SRD standard from the srd-doc server (`get_doc`) and obey every
   rule it states.
2. Interview the user for the gaps.
3. Write the SRD. Set the header `Status` to one of the standard's STA-1
   values, written exactly as the standard spells them; a new SRD starts at
   `IN PROGRESS`.

## Output

The path written and the open questions.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/srd/create.md`,
the sibling winning a conflict — a read-only install writes the second, and what
it learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule to the sibling when this directory
is writable, else to the fallback, creating it, and report where.
EOF_1
mkdir -p srd/evals/mocks/srd-doc/fixtures
cat > srd/evals/mocks/srd-doc/fixtures/srd-standard.md <<'EOF_2'
# SRD standard (frozen eval copy)

## Header

**STA-1:** The "Status" field MUST be one of: "IN PROGRESS", "PROPOSED",
"ACCEPTED", or "REJECTED".

**STA-2:** An SRD that requires changes to the UI MUST NOT have a "Status" of
"ACCEPTED" until its designs are linked.
EOF_2
