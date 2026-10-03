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
#   ./dev/eval-changed.sh --path srd/skills/edit   ... only changes under a path
#   ./dev/eval-changed.sh --skill srd/edit [--skill go/review]   whole skills
#   ./dev/eval-changed.sh --case srd 'edit--*' [--case srd 'review--x']  case globs
#   ./dev/eval-changed.sh --all srd       every case of a group
#   ./dev/eval-changed.sh --list-tags srd/edit
#   ./dev/eval-changed.sh --clean        delete leftover /tmp/claude-eval-* workspaces
#   -j N   concurrent runs (1-8, default 2: more burns the 5-hour usage
#          window faster); --dry-run prints, runs nothing
#   --max-usd N  stop once this invocation has spent N dollars (default 5);
#          a case costs $0.10-0.80, a fan-out case $3-9
#   --model M  run the cases on model M (e.g. sonnet for cheap calibration;
#          confirm on the default model before relying on a pass)
#   --keep keeps every run's workspace and trace (paths in the JSON); without
#          it the workspaces are deleted after the run
#
# Each failed case leaves its trace in <results>/<group>/failed/<case>.trace.jsonl
# and its last message is printed, so a failure needs no re-run to diagnose.
#
# Every run first checks the machine (git, node, go, gofmt; on Linux a bwrap
# sandbox that can start a shell) and stops with the fix if one is missing.
#
# Exit: 0 all selected cases pass, 1 a case failed or nothing could run.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

base=""
jobs=2
max_usd=5
dry=0
keep=0
declare -a explicit_skills=() all_groups=() case_args=() paths=() model=()

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
    --path) paths+=("$2"); shift 2 ;;
    --skill) explicit_skills+=("$2"); shift 2 ;;
    --all) all_groups+=("$2"); shift 2 ;;
    --case) case_args+=("$2" "$3"); shift 3 ;;
    --list-tags) list_tags "$2"; exit 0 ;;
    --clean)
        # Runs seal parts of their workspace read-only; unseal, then delete.
        for d in "${TMPDIR:-/tmp}"/claude-eval-*/; do
            [ -d "$d" ] || continue
            chmod -R u+rwx "$d" 2>/dev/null; rm -rf "$d"
        done
        exit 0 ;;
    -j) jobs="$2"; shift 2 ;;
    --max-usd) max_usd="$2"; shift 2 ;;
    --model) model=(--model "$2"); shift 2 ;;
    --dry-run) dry=1; shift ;;
    --keep) keep=1; shift ;;
    -h|--help) sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) die "unknown argument: $1 (see --help)" ;;
    esac
done

command -v claude >/dev/null || die "claude CLI not found"

# --- Preflight: the machine can run what the cases need. Checked every run,
# since a sysctl set with -w is gone after a reboot and a case whose shell
# fails can still pass on what it reads, hiding the gap. ---
preflight() {
    local missing=()
    for t in git node go gofmt; do
        command -v "$t" >/dev/null || missing+=("$t")
    done
    [ ${#missing[@]} -eq 0 ] || die "preflight: not on PATH: ${missing[*]}"
    # Runs get a fresh $HOME and no network, so Go fixtures resolve their
    # dependencies from this machine's module cache (served as GOPROXY below);
    # every module a fixture pins in its go.sum must already be there.
    local cache mod ver esc absent=()
    cache="$(go env GOMODCACHE)"
    while read -r mod ver; do
        esc="$(printf '%s' "$mod" | sed -E 's/[A-Z]/!\L&/g')"
        [ -f "$cache/cache/download/$esc/@v/$ver.zip" ] || absent+=("$mod@$ver")
    done < <(grep -ohE '^[[:space:]]*[a-z0-9.-]+\.[a-z]+/[^ ]+ v[^ /]+ h1:' \
        "$ROOT"/*/evals/*/scaffold.sh 2>/dev/null | awk '{print $1, $2}' | sort -u)
    [ ${#absent[@]} -eq 0 ] ||
        die "preflight: modules missing from $cache (fixtures need them; runs have no network): go mod download ${absent[*]}"
    [ "$(uname -s)" = Linux ] || return 0
    command -v bwrap >/dev/null || die "preflight: bwrap not found (the eval sandbox needs it; apt install bubblewrap)"
    # The sandbox runs each command through apply-seccomp, which opens a user
    # namespace nested inside bwrap's and needs a capability there. Ubuntu
    # blocks it two ways: the userns sysctl, and the bwrap-userns-restrict
    # AppArmor profile (children of bwrap get `deny capability`). Replay that
    # nesting; when it fails, every in-run shell command fails the same way.
    if ! bwrap --ro-bind / / --unshare-user --dev /dev --proc /proc \
        unshare --user --map-root-user true 2>/dev/null; then
        cat >&2 <<'EOF'
eval-changed: preflight: the eval sandbox cannot start a shell.
  A user namespace nested inside bwrap gets no capabilities, so every Bash call
  inside a case fails (apply-seccomp: write /proc/self/setgroups ...). Fix
  (see ONBOARDING.md, "Eval runs"):
    sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0
    echo 'kernel.apparmor_restrict_unprivileged_userns=0' |
        sudo tee /etc/sysctl.d/60-userns.conf
    sudo ln -sf /etc/apparmor.d/bwrap-userns-restrict /etc/apparmor.d/disable/
    sudo apparmor_parser -R /etc/apparmor.d/bwrap-userns-restrict
EOF
        exit 1
    fi
}
preflight

# Fixture Go modules: a case's scaffold (which runs outside the sandbox) fills
# the run's own module cache with `go mod download`, fetching from this
# machine's cache served as a file proxy. Inside the run the sandbox hides
# that path, but by then every pinned module is already in the run's cache.
GOPROXY="file://$(go env GOMODCACHE)/cache/download"
export GOPROXY

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
        git diff --name-only "$base" -- "${paths[@]}"
    else
        git diff --name-only HEAD -- "${paths[@]}"
        git ls-files -o --exclude-standard -- "${paths[@]}"
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

if [ ${#explicit_skills[@]} -eq 0 ] && [ ${#all_groups[@]} -eq 0 ] && [ ${#case_args[@]} -eq 0 ]; then
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
# Case globs expand here to case:<name> tags; every case carries its own (lint).
for ((i = 0; i < ${#case_args[@]}; i += 2)); do
    g="${case_args[i]}" glob="${case_args[i+1]}" n=0
    for d in "$g"/evals/$glob/; do
        [ -f "$d/prompt.md" ] || continue
        add "$g" "case:$(basename "$d")"; n=$((n + 1))
    done
    [ "$n" -gt 0 ] || die "no case in $g/evals matches '$glob'"
done

groups="$(printf '%s\n' "${!tags[@]}" "${!whole[@]}" | sed '/^$/d' | sort -u)"
[ -n "$groups" ] || { echo "eval-changed: no skill change found; lint is clean."; exit 0; }

# --- Run each group. ---
rc=0
out="$ROOT/tmp/eval-changed/$(date +%Y%m%dT%H%M%S)-$$"
mkdir -p "$out"
for g in $groups; do
    [ -d "$g/evals" ] || { echo "== $g: no native cases (lint only)"; continue; }
    declare -a sel=()
    if [ -n "${whole[$g]:-}" ]; then sel=()
    else
        for t in $(printf '%s\n' ${tags[$g]} | sort -u); do sel+=(--tag "$t"); done
    fi
    echo "== $g: ${sel[*]:-(all cases)}"
    [ "$dry" = 1 ] && continue
    json="$out/$g.json"
    left=$(python3 -c "print(round($max_usd - ${spent:-0}, 2))")
    if python3 -c "import sys; sys.exit(0 if $left <= 0 else 1)"; then
        echo "   skipped: --max-usd $max_usd spent"; rc=1; continue
    fi
    set +e
    claude plugin eval "./$g" "${sel[@]}" --runs 1 --ablation none --scaffold \
        --trust-plugin --no-publish -j "$jobs" --keep-temp "${model[@]}" \
        --max-cost-usd "$left" \
        --allow-tools Write Edit Bash LSP \
        --output-dir "$out/$g" --json "$json" >/dev/null 2>"$out/$g.err"
    r=$?
    set -e
    [ -s "$json" ] && spent=$(python3 -c "import json; print(${spent:-0} + json.load(open('$json')).get('costUsd', 0))")
    [ "$r" = 2 ] && echo "   stopped at the --max-usd $max_usd ceiling (partial results)"
    if [ ! -s "$json" ]; then
        grep -v '^Note:' "$out/$g.err" | head -5
        echo "   no cases ran (see $out/$g.err)"; rc=1; continue
    fi
    python3 - "$json" "$out/$g/failed" "$keep" <<'PY' || rc=1
import json, os, shutil, subprocess, sys
d = json.load(open(sys.argv[1]))
failed_dir, keep = sys.argv[2], sys.argv[3] == "1"
bad = 0

def last_message(trace):
    text = ""
    for line in open(trace):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("type") == "result" and e.get("result"):
            text = e["result"]
        elif e.get("type") == "assistant":
            parts = [b.get("text", "") for b in e["message"].get("content", [])
                     if b.get("type") == "text"]
            if any(parts):
                text = "\n".join(parts)
    return text

for c in d["cases"]:
    for r in c["arms"]["with"]:
        ok = r.get("passed") and not r.get("error")
        bad += not ok
        # A run cut off by the account's usage limit says nothing about the
        # skill: label it so it is re-run, never triaged as a defect.
        limit = "limit" in (r.get("error") or "").lower()
        verdict = "PASS" if ok else ("LIMIT" if limit else "FAIL")
        print(f"   {verdict}  {c['name']}  ({r.get('durationSeconds', '?')}s)")
        if limit:
            print(f"         {r['error']} — re-run; graders not meaningful")
            continue
        if r.get("error"):
            print(f"         error: {r['error']}")
        for gr in r.get("graders", []):
            if not gr.get("passed"):
                why = (gr.get("evidence") or gr.get("explanation") or "").replace("\n", " ")
                print(f"         {gr['name']}: {why[:200]}")
        trace = r.get("tracePath") or ""
        if not ok and os.path.isfile(trace):
            os.makedirs(failed_dir, exist_ok=True)
            kept = os.path.join(failed_dir, f"{c['name']}.trace.jsonl")
            shutil.copyfile(trace, kept)
            msg = last_message(trace).strip().replace("\n", "\n         | ")
            print(f"         last message:\n         | {msg[:1500]}")
            print(f"         trace: {kept}")
        tmp = os.path.dirname(os.path.dirname(trace))
        if not keep and os.path.basename(tmp).startswith("claude-eval-"):
            # The run seals parts of its workspace read-only; unseal, then delete.
            subprocess.run(["chmod", "-R", "u+rwx", tmp], stderr=subprocess.DEVNULL)
            shutil.rmtree(tmp, ignore_errors=True)
a = d["aggregates"]
print(f"   {a['casesPassed']}/{a['casesTotal']} passed, "
      f"{d['durationSeconds']}s, ${d['costUsd']:.2f}")
sys.exit(1 if bad else 0)
PY
    [ "$r" = 0 ] || rc=1
done
# A history_file run leaves a session file (UUID name) beside the history; it
# holds the runner's full system prompt, so it must not linger.
git ls-files -o -i --exclude-standard -- '*/evals/*' |
    grep -E '/[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}\.jsonl$' | xargs -r rm -f || true
echo "results: $out"
exit "$rc"
