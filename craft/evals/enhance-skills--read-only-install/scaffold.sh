#!/usr/bin/env bash
set -euo pipefail
mkdir -p home/.claude/plugins/cache/ctx42-skills/craft/skills/cm
cat > home/.claude/plugins/cache/ctx42-skills/craft/skills/cm/SKILL.md <<'EOF_0'
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
EOF_0
