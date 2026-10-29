#!/usr/bin/env bash
# eval-routine.sh — the routine check after a skill edit, in one command.
#
# Lint first (free; a lint error stops here), then in parallel: every probe
# (cached by input, so only changed skills cost anything), the trigger test
# (free while no description changed), and the ambiguity hunt on the skills
# whose text changed against --base (default HEAD, working tree). Wall time
# is the slowest of the three, not their sum. Outputs print in order once all
# finish. Agent-run cases and blind rounds are never part of it.
#
# Usage:
#   scripts/eval-routine.sh                 against HEAD (uncommitted changes)
#   scripts/eval-routine.sh --base REF      against REF
# Exit: non-zero when lint fails or any tool reports a FAIL, SPLIT, or split.
set -uo pipefail
# The repo under test: $SKILL_EVAL_ROOT, else the git top level of the working
# directory (the script ships inside the skill-eval skill, not the repo).
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(realpath "${SKILL_EVAL_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}")"
export SKILL_EVAL_ROOT="$ROOT"
base=HEAD
[ "${1:-}" = --base ] && base="$2"
t0=$(date +%s)
"$HERE/lint-skills.sh" >/dev/null 2>&1 || {
    "$HERE/lint-skills.sh" | grep -E '^ERR'; echo "eval-routine: lint failed"; exit 1
}
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
"$HERE/eval-probe.py" >"$tmp/probe" 2>&1 & p1=$!
"$HERE/eval-triggers.py" >"$tmp/triggers" 2>&1 & p2=$!
"$HERE/eval-hunt.py" --base "$base" >"$tmp/hunt" 2>&1 & p3=$!
rc=0
for p in $p1 $p2 $p3; do wait "$p" || rc=1; done
# Probes print one PASS line each; show only what is not a pass.
grep -vE '^   PASS ' "$tmp/probe"
cat "$tmp/triggers" "$tmp/hunt"
cost=$(cat "$tmp"/* | grep -oE '\$[0-9]+\.[0-9]+, [0-9]+s' | awk -F'[$,]' '{s+=$2} END {printf "%.2f", s}')
echo "eval-routine: lint ok; \$$cost; $(( $(date +%s) - t0 ))s wall"
exit "$rc"
