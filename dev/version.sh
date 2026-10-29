#!/usr/bin/env bash
# Keeps every plugin/marketplace manifest version in lockstep with the VER file.
#
# VER is the single source of truth for the version. The manifests
# (*/​.claude-plugin/plugin.json and .claude-plugin/marketplace.json) carry the
# same number without the leading "v" and are DERIVED — never edited by hand. A
# stale manifest version silently blocks `claude plugin update`, so this script
# propagates VER into them and checks that they agree.
#
# The .githooks/pre-commit hook runs `sync` on any commit that changes VER, so a
# version bump updates VER, CHANGELOG, and all manifests atomically in one commit
# and tag. This script never changes the version itself — it only mirrors VER.
#
# Subcommands:
#   verify         Exit non-zero if any manifest version != VER. Used by
#                  lint-skills.sh as a drift backstop.
#   sync           Write VER's number into every manifest. Idempotent; the
#                  pre-commit hook calls this when VER is staged.
#   manifests      Print the absolute path of every version-bearing JSON file,
#                  one per line. Used by the hook to stage the synced files.
#   install-hooks  Point git at the tracked .githooks/ directory (one-time,
#                  per clone) so the pre-commit sync runs for this repo.
#
# No external dependencies (pure bash + coreutils; no jq). Exit status is 0 on
# success, non-zero on drift or bad input, so a failure aborts the commit that
# triggered it (fail closed — never drift).
set -euo pipefail

# The script lives in dev/; the repo root is one level up.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VER_FILE="$ROOT/VER"
MARKETPLACE="$ROOT/.claude-plugin/marketplace.json"

die() { echo "version.sh: error: $*" >&2; exit 2; }

[ -f "$VER_FILE" ] || die "no VER file at $VER_FILE"

# Numeric version only, e.g. "0.1.1" — the form stored in the JSON manifests.
# VER itself carries a leading "v" (e.g. "v0.1.1"), set by the version bump.
num_ver() { local v; v="$(cat "$VER_FILE")"; printf '%s' "${v#v}"; }

# Print the first top-level "version": "..." string value from a JSON manifest.
# The manifests carry "version" as a top-level key and it is the first "version"
# in each file, so the first match is the value jq's '.version' returned. Prints
# nothing when the key is absent.
json_version() {
    grep -oE '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$1" \
        | head -1 | sed -E 's/.*"([^"]*)"[[:space:]]*$/\1/'
}

# Every JSON file that carries a "version" key, absolute paths, one per line:
# marketplace first, then each plugin manifest.
cmd_manifests() {
    printf '%s\n' "$MARKETPLACE"
    find "$ROOT" -path '*/.claude-plugin/plugin.json' | sort
}

cmd_verify() {
    local want bad=0 f cur
    want="$(num_ver)"
    while IFS= read -r f; do
        [ -f "$f" ] || { echo "MISSING ${f#"$ROOT"/}"; bad=1; continue; }
        cur="$(json_version "$f")"
        if [ "$cur" != "$want" ]; then
            echo "DRIFT  ${f#"$ROOT"/}: '$cur' != VER '$want'"
            bad=1
        fi
    done < <(cmd_manifests)
    [ "$bad" -eq 0 ] && echo "OK  all manifests == $want (v$want)"
    return "$bad"
}

cmd_sync() {
    local want f changed=0
    want="$(num_ver)"
    while IFS= read -r f; do
        [ -f "$f" ] || die "missing manifest $f"
        if [ "$(json_version "$f")" = "$want" ]; then continue; fi
        # Surgically rewrite only the top-level "version" value line, so the
        # rest of the file's formatting (e.g. inline arrays) is left untouched.
        # 0,/re/ restricts the substitution to the first matching line (GNU sed).
        sed -i -E \
            "0,/^([[:space:]]*\"version\"[[:space:]]*:[[:space:]]*\")[^\"]*(\".*)$/s//\\1$want\\2/" \
            "$f"
        # Trust nothing: confirm the version line now reads the wanted value.
        [ "$(json_version "$f")" = "$want" ] \
            || die "failed to set version in $f (check for a nested 'version' key)"
        echo "set ${f#"$ROOT"/} -> $want"
        changed=1
    done < <(cmd_manifests)
    [ "$changed" -eq 0 ] && echo "manifests already at $want"
    return 0
}

cmd_install_hooks() {
    [ -d "$ROOT/.githooks" ] || die "no .githooks/ directory at $ROOT"
    git -C "$ROOT" config core.hooksPath .githooks
    chmod +x "$ROOT"/.githooks/* 2>/dev/null || true
    echo "core.hooksPath set to .githooks (pre-commit version sync active)"
}

case "${1:-}" in
    verify)        shift; cmd_verify "$@" ;;
    sync)          shift; cmd_sync "$@" ;;
    manifests)     shift; cmd_manifests "$@" ;;
    install-hooks) shift; cmd_install_hooks "$@" ;;
    *) die "usage: version.sh {verify|sync|manifests|install-hooks}" ;;
esac
