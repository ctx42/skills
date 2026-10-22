#!/usr/bin/env bash
set -euo pipefail
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
mkdir -p craft/skills/cm
cat > craft/skills/cm/SKILL.md <<'EOF_0'
---
name: cm
description: >
  Writes git commit messages (Conventional Commits).
license: MIT
---

# cm

## Usage

```
/cm   write a commit message for the staged change
```

## Steps

1. Read the staged diff (`git diff --cached`).
2. Write the summary line, then the body.
3. Show the message; commit only when asked.

## Summary line

- Type: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `chore`.
- Scope: optional, short noun.
- Description: imperative, lowercase, no period, at most 72 chars.

## Body

- Wrap at 72 columns; explain why, the diff shows what.
- No Co-Authored-By trailer.

## Output

Report tersely: no preamble or narration. Print the message in one fenced
block.

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
mkdir -p craft/skills/cm
cat > craft/skills/cm/LESSONS.md <<'EOF_1'
# Lessons

Rules learned for the `cm` skill. Read before running; obey each line.

- Derive the commit type from the diff, never the branch name.
- For acme-billing, use the scope `billing` because PR #412 touched
  `export.go`.
- Never add a Co-Authored-By trailer.
EOF_1
git add -A
git commit -qm initial
sed -i 's/^- Scope: optional, short noun\.$/&\n- For acme-billing, scope invoice-export changes `billing`./' craft/skills/cm/SKILL.md
grep -q 'acme-billing' craft/skills/cm/SKILL.md
