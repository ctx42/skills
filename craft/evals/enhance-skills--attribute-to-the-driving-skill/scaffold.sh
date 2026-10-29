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

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/craft/cm.md` (pass `~` as
is, the file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable. A missing file needs no comment. On a correction or self-caught
mistake, append a one-line rule — general, naming nothing from the project at
hand (its files, tests, tickets) — to the sibling when this directory is
writable, else to the fallback, creating it, and report where.
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

1. Load the SRD standard from the srd server (`get_doc`) and obey every
   rule it states.
2. Interview the user for the gaps.
3. Write the SRD. Set the header `Lifecycle` to one of the standard's LIF-1
   values, written exactly as the standard spells them; a new SRD starts at
   `DRAFT`.

## Output

The path written and the open questions.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/srd/create.md` (pass `~` as
is, the file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable. A missing file needs no comment. On a correction or self-caught
mistake, append a one-line rule — general, naming nothing from the project at
hand (its files, tests, tickets) — to the sibling when this directory is
writable, else to the fallback, creating it, and report where.
EOF_1
mkdir -p srd/evals/mocks/srd/fixtures
cat > srd/evals/mocks/srd/fixtures/srd-standard.md <<'EOF_2'
# SRD standard (frozen eval copy)

## Header

**LIF-1:** "Lifecycle" MUST hold one of "DRAFT", "IN REVIEW", "APPROVED", or
"WITHDRAWN".

**LIF-2:** An SRD whose "Mockups" is not "none" MUST NOT be "APPROVED" before
its mockup set is signed off.
EOF_2
