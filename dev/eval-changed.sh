#!/usr/bin/env bash
# eval-changed.sh — run the native eval cases a change reaches, in minutes.
#
# Maps the working-tree diff (or --base REF..) to tags and runs
# `claude plugin eval` once per plugin group with those tags (tags OR):
#
#   <group>/skills/<skill>/SKILL.md  changed line under `## X` -> sec:<skill>:<x>
#                                    changed line above the first `## ` -> skill:<skill>
#   <group>/skills/<skill>/references/<r>.md                    -> ref:<skill>/<r>
#   <group>/skills/<skill>/{LESSONS.md,assets/*,evals/*}         -> skill:<skill>
#   <group>/evals/<case>/**                                     -> case:<case>
#   <group>/evals/mocks/**                                      -> every case of the group
#
# A case lists every tag it exercises in its prompt.md frontmatter
# (`--list-tags <group>/<skill>` prints the section and reference tags).
# Native cases live in <group>/evals/<case>/; see dev/eval/native-cases.md.
#
# Usage:
#   ./dev/eval-changed.sh                 cases reached by uncommitted changes
#   ./dev/eval-changed.sh --base HEAD~3   ... by changes since HEAD~3
#   ./dev/eval-changed.sh --skill srd/edit [--skill go/review]   whole skills
#   ./dev/eval-changed.sh --case srd 'edit--*'                   a case glob
#   ./dev/eval-changed.sh --all srd       every case of a group
#   ./dev/eval-changed.sh --list-tags srd/edit
#   -j N   concurrent runs (1-8, default 8); --dry-run prints, runs nothing
#   --keep keeps each run's workspace and trace for diagnosis (paths in the JSON)
#
# Exit: 0 all selected cases pass, 1 a case failed or nothing could run.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

base=""
jobs=8
dry=0
keep=()
declare -a explicit_skills=() all_groups=()
case_group="" case_glob=""

die() { echo "eval-changed: $*" >&2; exit 1; }

slug() { tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g'; }

list_tags() {
    local dir="$ROOT/${1%%/*}/skills/${1#*/}" skill
    skill="$(basename "$dir")"
    [ -f "$dir/SKILL.md" ] || die "no SKILL.md in $dir"
    echo "skill:$skill"
    grep -E '^## ' "$dir/SKILL.md" | sed 's/^## //' | while read -r h; do
        echo "sec:$skill:$(printf '%s' "$h" | slug)"
    done
    if [ -d "$dir/references" ]; then
        for r in "$dir"/references/*.md; do
            [ -e "$r" ] && echo "ref:$skill/$(basename "$r" .md)"
        done
    fi
}

while [ $# -gt 0 ]; do
    case "$1" in
    --base) base="$2"; shift 2 ;;
    --skill) explicit_skills+=("$2"); shift 2 ;;
    --all) all_groups+=("$2"); shift 2 ;;
    --case) case_group="$2"; case_glob="$3"; shift 3 ;;
    --list-tags) list_tags "$2"; exit 0 ;;
    -j) jobs="$2"; shift 2 ;;
    --dry-run) dry=1; shift ;;
    --keep) keep=(--keep-temp); shift ;;
    -h|--help) sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) die "unknown argument: $1 (see --help)" ;;
    esac
done

command -v claude >/dev/null || die "claude CLI not found"

# --- Tier 0: lint first; a lint error stops the run. ---
"$ROOT/dev/lint-skills.sh" >/dev/null 2>&1 || {
    "$ROOT/dev/lint-skills.sh" | grep -E '^ERR' || true
    die "lint failed; fix it before running evals"
}

# --- Collect tags per group. ---
declare -A tags=()   # group -> space-separated tags
declare -A whole=()  # group -> 1 when every case of the group runs
add() { tags[$1]="${tags[$1]:-} $2"; }

changed_files() {
    if [ -n "$base" ]; then
        git diff --name-only "$base"
    else
        git diff --name-only HEAD
        git ls-files -o --exclude-standard
    fi
}

changed_lines() { # file -> changed line numbers in the current version
    local range
    if [ -n "$base" ]; then range="$base"; else range="HEAD"; fi
    if ! git cat-file -e "$range:$1" 2>/dev/null; then
        seq 1 "$(wc -l <"$1")"; return
    fi
    git diff -U0 "$range" -- "$1" | sed -nE 's/^@@ -[0-9,]+ \+([0-9]+)(,([0-9]+))? @@.*/\1 \3/p' |
        while read -r start count; do
            count="${count:-1}"
            [ "$count" = 0 ] && count=1   # pure deletion: the line after it
            seq "$start" $((start + count - 1))
        done
}

map_skill_md() { # group skill file
    local g="$1" s="$2" f="$3" n heading
    while read -r n; do
        heading="$(head -n "$n" "$f" | grep -E '^## ' | tail -1 | sed 's/^## //')"
        if [ -z "$heading" ]; then add "$g" "skill:$s"
        else add "$g" "sec:$s:$(printf '%s' "$heading" | slug)"; fi
    done < <(changed_lines "$f")
}

if [ ${#explicit_skills[@]} -eq 0 ] && [ ${#all_groups[@]} -eq 0 ] && [ -z "$case_group" ]; then
    while read -r f; do
        [ -n "$f" ] || continue
        IFS=/ read -r g p1 p2 p3 p4 <<<"$f"
        [ -f "$g/.claude-plugin/plugin.json" ] || continue
        if [ "$p1" = skills ] && [ -n "$p2" ]; then
            if [ "$p3" = SKILL.md ] && [ -f "$f" ]; then map_skill_md "$g" "$p2" "$f"
            elif [ "$p3" = references ] && [ -n "$p4" ]; then add "$g" "ref:$p2/${p4%.md}"
            else add "$g" "skill:$p2"; fi
        elif [ "$p1" = evals ] && [ "$p2" = mocks ]; then whole[$g]=1
        elif [ "$p1" = evals ] && [ -n "$p2" ] && [ "$p2" != results ] && [ "$p2" != fixtures ]; then
            add "$g" "case:$p2"
        elif [ "$p1" = evals ] && [ "$p2" = fixtures ]; then whole[$g]=1
        fi
    done < <(changed_files | sort -u)
fi
for s in "${explicit_skills[@]}"; do add "${s%%/*}" "skill:${s#*/}"; done
for g in "${all_groups[@]}"; do whole[$g]=1; done

groups="$(printf '%s\n' "${!tags[@]}" "${!whole[@]}" "$case_group" | sed '/^$/d' | sort -u)"
[ -n "$groups" ] || { echo "eval-changed: no skill change found; lint is clean."; exit 0; }

# --- Run each group. ---
rc=0
out="$ROOT/tmp/eval-changed/$(date +%Y%m%dT%H%M%S)-$$"
mkdir -p "$out"
for g in $groups; do
    [ -d "$g/evals" ] || { echo "== $g: no native cases (lint only)"; continue; }
    declare -a sel=()
    if [ -n "${whole[$g]:-}" ]; then sel=()
    elif [ "$g" = "$case_group" ]; then sel=(--case "$case_glob")
    else
        for t in $(printf '%s\n' ${tags[$g]} | sort -u); do sel+=(--tag "$t"); done
    fi
    echo "== $g: ${sel[*]:-(all cases)}"
    [ "$dry" = 1 ] && continue
    json="$out/$g.json"
    set +e
    claude plugin eval "./$g" "${sel[@]}" --runs 1 --ablation none --scaffold \
        --trust-plugin --no-publish -j "$jobs" "${keep[@]}" \
        --allow-tools Write Edit Bash LSP \
        --output-dir "$out/$g" --json "$json" >/dev/null 2>"$out/$g.err"
    r=$?
    set -e
    if [ ! -s "$json" ]; then
        grep -v '^Note:' "$out/$g.err" | head -5
        echo "   no cases ran (see $out/$g.err)"; rc=1; continue
    fi
    python3 - "$json" <<'PY' || rc=1
import json, sys
d = json.load(open(sys.argv[1]))
bad = 0
for c in d["cases"]:
    r = c["arms"]["with"][0]
    ok = r.get("passed") and not r.get("error")
    bad += not ok
    print(f"   {'PASS' if ok else 'FAIL'}  {c['name']}  ({r.get('durationSeconds', '?')}s)")
    if r.get("error"):
        print(f"         error: {r['error']}")
    for gr in r.get("graders", []):
        if not gr.get("passed"):
            why = (gr.get("evidence") or gr.get("explanation") or "").replace("\n", " ")
            print(f"         {gr['name']}: {why[:200]}")
a = d["aggregates"]
print(f"   {a['casesPassed']}/{a['casesTotal']} passed, "
      f"{d['durationSeconds']}s, ${d['costUsd']:.2f}")
sys.exit(1 if bad else 0)
PY
    [ "$r" = 0 ] || rc=1
done
echo "results: $out"
exit "$rc"
