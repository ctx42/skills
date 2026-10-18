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
