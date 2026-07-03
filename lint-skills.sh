#!/usr/bin/env bash
# Lints every skill in this repo against the authoring standard
# (skill-smith/standards.md). Mechanical checks only — it never edits files.
#
# A "skill" is any directory containing a SKILL.md. For each
# skill this script checks:
#   - SKILL.md and README.md both exist,
#   - frontmatter has name + description, name equals the directory name, and
#     carries no forbidden platform-extension keys (strict-portable rule),
#   - the body uses no dynamic injection (!`cmd`) or $ARGUMENTS / $N,
#   - README.md has an `## Evaluations` section,
#   - every bundled .md reference over ~100 lines starts with a Contents list.
#
# It then cross-checks .claude-plugin/marketplace.json (if present): every plugin
# `source` must be a real plugin directory (with .claude-plugin/plugin.json), and
# every skill on disk must live under exactly one plugin's skills/ directory.
# Skipped with a warning if jq is missing.
#
# Exit status is 0 when clean, 1 when any error is found. Warnings do not fail.
set -euo pipefail
shopt -s nullglob

SKILLS_SRC="$(cd "$(dirname "$0")" && pwd)"
MARKETPLACE="$SKILLS_SRC/.claude-plugin/marketplace.json"

# Frontmatter keys that break Grok/Claude portability (standards.md).
FORBIDDEN_KEYS=(
    user-invocable user_invocable disable-model-invocation when_to_use
    arguments argument-hint context agent allowed-tools disallowed-tools
)

errors=0
warnings=0

err()  { echo "ERROR  $1"; errors=$((errors + 1)); }
warn() { echo "WARN   $1"; warnings=$((warnings + 1)); }

# Print the YAML frontmatter block (between the first two --- lines) of a file.
frontmatter() {
    awk 'NR==1 && $0=="---"{f=1; next} f && $0=="---"{exit} f' "$1"
}

lint_skill() {
    local dir="$1" name skill_md readme fm
    name="$(basename "$dir")"
    skill_md="$dir/SKILL.md"
    readme="$dir/README.md"

    [ -f "$readme" ] || err "$name: missing README.md"

    fm="$(frontmatter "$skill_md")"

    # name + description present.
    grep -qE '^name:[[:space:]]' <<<"$fm" \
        || err "$name: frontmatter missing 'name:'"
    grep -qE '^description:[[:space:]]*([|>].*)?$|^description:[[:space:]]*\S' \
        <<<"$fm" || err "$name: frontmatter missing 'description:'"

    # name equals directory name.
    local declared
    declared="$(grep -E '^name:[[:space:]]' <<<"$fm" \
        | head -1 | sed -E 's/^name:[[:space:]]*//; s/[[:space:]]*$//')"
    [ "$declared" = "$name" ] \
        || err "$name: frontmatter name '$declared' != directory '$name'"

    # No forbidden frontmatter keys.
    local key
    for key in "${FORBIDDEN_KEYS[@]}"; do
        grep -qE "^${key}:" <<<"$fm" \
            && err "$name: forbidden frontmatter key '$key'"
    done

    # Body must not use dynamic injection or argument substitution. Dynamic
    # injection is !`cmd` — a bang then a backtick opening a command; a
    # backtick-quoted bang (`!`) is fine, so require a command char after.
    grep -qE '!`[^`[:space:]]' "$skill_md" \
        && err "$name: SKILL.md uses dynamic injection (!\`cmd\`)"
    grep -qE '\$ARGUMENTS|\$[0-9]' "$skill_md" \
        && err "$name: SKILL.md uses \$ARGUMENTS / \$N substitution"

    # README has an Evaluations section.
    if [ -f "$readme" ]; then
        grep -qE '^##[[:space:]]+Evaluations' "$readme" \
            || err "$name: README.md has no '## Evaluations' section"
    fi

    # Bundled .md references over ~100 lines start with a Contents list.
    local f lines
    for f in "$dir"/*.md "$dir"/references/*.md "$dir"/assets/*.md; do
        [ -f "$f" ] || continue
        case "$(basename "$f")" in SKILL.md|README.md) continue ;; esac
        lines="$(wc -l <"$f")"
        if [ "$lines" -gt 100 ]; then
            head -25 "$f" | grep -qiE '^#+[[:space:]]+Contents|^Contents' \
                || warn "${f#"$SKILLS_SRC"/}: $lines lines, no Contents list"
        fi
    done
}

# Cross-check the plugin marketplace against the skills on disk: every plugin
# `source` must be a real plugin directory, and every skill must live under
# exactly one plugin's skills/ dir. SKILL_PATHS is the set of skill directories
# (relative to the repo root) collected by the main loop.
check_marketplace() {
    [ -f "$MARKETPLACE" ] || {
        warn "no .claude-plugin/marketplace.json — skipping marketplace checks"
        return
    }
    if ! command -v jq >/dev/null 2>&1; then
        warn "jq not found — skipping marketplace/skill consistency checks"
        return
    fi
    if ! jq empty "$MARKETPLACE" 2>/dev/null; then
        err "marketplace.json: invalid JSON"
        return
    fi

    # Collect plugin sources (leading "./" stripped) and validate each one is a
    # real plugin directory carrying a manifest.
    local -a sources=()
    local name src
    while IFS=$'\t' read -r name src; do
        src="${src#./}"
        sources+=("$src")
        [ -f "$SKILLS_SRC/$src/.claude-plugin/plugin.json" ] \
            || err "marketplace: plugin '$name' source '$src' has no .claude-plugin/plugin.json"
    done < <(jq -r '.plugins[] | "\(.name)\t\(.source)"' "$MARKETPLACE")

    # Every skill on disk must sit under exactly one plugin source's skills/ dir.
    local sp hits
    for sp in "${SKILL_PATHS[@]}"; do
        hits=0
        for src in "${sources[@]}"; do
            case "$sp" in "$src"/skills/*) hits=$((hits + 1)) ;; esac
        done
        [ "$hits" -eq 1 ] \
            || err "skill '$sp' sits under $hits plugin sources (want exactly 1)"
    done
}

declare -a SKILL_PATHS=()
while IFS= read -r skill_md; do
    dir="$(dirname "$skill_md")"
    SKILL_PATHS+=("${dir#"$SKILLS_SRC"/}")
    lint_skill "$dir"
done < <(find "$SKILLS_SRC" -name SKILL.md | sort)

check_marketplace

echo "----"
echo "$errors error(s), $warnings warning(s)."
[ "$errors" -eq 0 ]
