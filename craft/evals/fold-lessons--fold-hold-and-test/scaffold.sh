#!/usr/bin/env bash
set -euo pipefail
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
mkdir -p craft/skills/plan-smith
cat > craft/skills/plan-smith/SKILL.md <<'EOF_0'
---
name: plan-smith
description: >
  Writes and tracks an implementation plan.
license: MIT
---

# plan-smith

## Usage

```
/plan-smith <file>   write or update the plan in <file>
```

## Steps

1. Read the plan file, or start one.
2. Write numbered checkbox items.
3. Keep the status table in step: Y implemented, N not yet, X rejected.

## Status table

- One row per item, in item order.
- Update a row when its item's state changes.

## Output

Report tersely: no preamble or narration. Name the file written. Never paste
the plan back into chat.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/craft/plan-smith.md` (pass `~` as
is, the file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable. A missing file needs no comment. On a correction or self-caught
mistake, append a one-line rule — general, naming nothing from the project at
hand (its files, tests, tickets) — to the sibling when this directory is
writable, else to the fallback, creating it, and report where.
EOF_0
mkdir -p craft/skills/plan-smith
cat > craft/skills/plan-smith/LESSONS.md <<'EOF_1'
# Lessons

Rules learned for the `plan-smith` skill. Read before running; obey each line.

- Mark a rejected item X in the status table, never delete its row.
- Paste the whole plan back into chat after every update.
EOF_1
mkdir -p dev
cat > dev/lint-skills.sh <<'EOF_2'
#!/usr/bin/env bash
mkdir -p tmp && date +%s%N > tmp/.ran-lint
echo "0 error(s), 0 warning(s)."
EOF_2
chmod +x dev/lint-skills.sh
mkdir -p dev
cat > dev/eval-routine.sh <<'EOF_3'
#!/usr/bin/env bash
./dev/lint-skills.sh >/dev/null && date +%s%N > tmp/.ran-routine
echo "probes: all PASS"
echo "hunt: no splits"
echo 'eval-routine: lint ok; $0.12; 41s wall'
EOF_3
chmod +x dev/eval-routine.sh
mkdir -p dev
cat > dev/eval-probe.py <<'EOF_4'
#!/usr/bin/env python3
import sys
red = "--against" in sys.argv
print(("   FAIL " if red else "   PASS ") + " ".join(sys.argv[1:]))
print("probes: $0.02, 9s")
EOF_4
chmod +x dev/eval-probe.py
cat > .gitignore <<'EOF_5'
tmp/
EOF_5
git add -A
git commit -qm initial
