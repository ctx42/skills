#!/usr/bin/env bash
# Lints every skill in this repo against the authoring standard
# (skill-smith/standards.md). Mechanical checks only — it never edits files.
#
# A "skill" is any directory containing a SKILL.md. For each
# skill this script checks:
#   - SKILL.md and README.md both exist,
#   - frontmatter has name + description, name equals the directory name, and
#     carries no forbidden platform-extension keys (strict-portable rule),
#   - the description stays near the ~350-char aim (warns past 500) and uses
#     no first/second person (warning only),
#   - the body uses no dynamic injection (!`cmd`) or $ARGUMENTS / $N,
#   - the body carries the output-discipline line ("Report tersely" or the
#     "no preamble or narration" phrasing),
#   - the body has a `## Self-learning` block (warning only),
#   - README.md has an `## Evaluations` section,
#   - every bundled .md reference over ~100 lines starts with a Contents list,
#   - Markdown prose wraps at ~80 columns (warning only).
#
# It then cross-checks .claude-plugin/marketplace.json (if present): every plugin
# `source` must be a real plugin directory (with .claude-plugin/plugin.json), and
# every skill on disk must live under exactly one plugin's skills/ directory.
# On machines with the vr checkout it also runs dev/sync-srd-standard.sh
# (warning only) to catch drift between srd-standard.md and its Confluence
# source.
#
# No external dependencies (pure bash + coreutils; no jq).
#
# Exit status is 0 when clean, 1 when any error is found. Warnings do not fail.
set -euo pipefail
shopt -s nullglob

# The script lives in dev/; the repo root is one level up.
SKILLS_SRC="$(cd "$(dirname "$0")/.." && pwd)"
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

# The house wrap: Markdown prose lines stay within ~80 columns (standards.md,
# Content hygiene). 80 is the target; lines up to a few over are tolerated only
# when unbreakable, which the heuristic below already exempts.
WRAP_LIMIT=80

# Warn on Markdown prose wider than WRAP_LIMIT. Skips fenced code blocks and
# table rows (aligned columns legitimately run wide), and flags a line only when
# it stays breakable past the limit — a space at or after the limit means it
# could have wrapped. Long URLs, paths, and links (no trailing space) are exempt.
# Width is display columns, not bytes: each UTF-8 multibyte sequence (arrows,
# em-dashes, …) collapses to one column first, since mawk's length() counts
# bytes. Rare double-width glyphs (emoji) undercount by one — acceptable slack.
check_wrap() {
    local f="$1" out
    [ -f "$f" ] || return 0
    out="$(awk -v L="$WRAP_LIMIT" '
        /^[[:space:]]*```/ { fence = !fence; next }
        fence              { next }
        /^[[:space:]]*\|/   { next }
        {
            s = $0
            gsub(/[\300-\367][\200-\277]*/, ".", s)
            if (length(s) <= L) next
            if (substr(s, L + 1) ~ / /) printf "%d (%d cols)\n", NR, length(s)
        }
    ' "$f")"
    [ -n "$out" ] || return 0
    local line
    while IFS= read -r line; do
        warn "${f#"$SKILLS_SRC"/}:$line exceeds ${WRAP_LIMIT}-col wrap"
    done <<<"$out"
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

    # Description size and point of view (standards.md, Description quality).
    # The aim is ~350 chars; warn only past 500 so a trigger-rich description
    # has headroom. Joins a folded/plain scalar into one string first.
    local desc
    desc="$(awk '
        /^description:/ {
            d = 1
            sub(/^description:[[:space:]]*[>|]?[[:space:]]*/, "")
            if (length($0)) printf "%s ", $0
            next
        }
        d && /^[a-zA-Z_-]+:/ { d = 0 }
        d { sub(/^[[:space:]]+/, ""); printf "%s ", $0 }
    ' <<<"$fm")"
    desc="${desc% }"
    [ "${#desc}" -gt 500 ] \
        && warn "$name: description is ${#desc} chars (aim <= ~350)"
    grep -qiE '(^|[^a-zA-Z])(I|you|your)([^a-zA-Z]|$)' <<<"$desc" \
        && warn "$name: description uses first/second person"

    # Body must not use dynamic injection or argument substitution. Dynamic
    # injection is !`cmd` — a bang then a backtick opening a command; a
    # backtick-quoted bang (`!`) is fine, so require a command char after.
    grep -qE '!`[^`[:space:]]' "$skill_md" \
        && err "$name: SKILL.md uses dynamic injection (!\`cmd\`)"
    grep -qE '\$ARGUMENTS|\$[0-9]' "$skill_md" \
        && err "$name: SKILL.md uses \$ARGUMENTS / \$N substitution"

    # Body carries the output-discipline line (standards.md mandates it; the
    # canonical wording is "Report tersely: …", grill-me embeds the phrasing).
    grep -qiE 'report tersely|no preamble or narration' "$skill_md" \
        || err "$name: SKILL.md lacks the output-discipline line"

    # Body carries the Self-learning block (every skill in this repo does).
    grep -q '^## Self-learning' "$skill_md" \
        || warn "$name: SKILL.md has no '## Self-learning' block"

    # README has an Evaluations section.
    if [ -f "$readme" ]; then
        grep -qE '^##[[:space:]]+Evaluations' "$readme" \
            || err "$name: README.md has no '## Evaluations' section"
    fi

    # Every Markdown file in the skill wraps prose at ~80 columns.
    check_wrap "$skill_md"
    check_wrap "$readme"

    # Bundled .md references over ~100 lines start with a Contents list, and
    # wrap like every other Markdown file.
    local f lines
    for f in "$dir"/*.md "$dir"/references/*.md "$dir"/assets/*.md; do
        [ -f "$f" ] || continue
        case "$(basename "$f")" in SKILL.md|README.md) continue ;; esac
        check_wrap "$f"
        lines="$(wc -l <"$f")"
        if [ "$lines" -gt 100 ]; then
            head -25 "$f" | grep -qiE '^#+[[:space:]]+Contents|^Contents' \
                || warn "${f#"$SKILLS_SRC"/}: $lines lines, no Contents list"
        fi
    done
}

# Print "name<TAB>source" for each object in the marketplace's "plugins" array,
# one per line. Replaces `jq -r '.plugins[] | "\(.name)\t\(.source)"'` without a
# JSON dependency: it relies on the manifest's well-formed layout — each plugin
# object lists "name" before "source" — which the marketplace file guarantees.
plugin_entries() {
    awk '
        # Return the first double-quoted string value on a "key": "value" line.
        function strval(s) {
            sub(/^[^:]*:[[:space:]]*"/, "", s)
            sub(/".*/, "", s)
            return s
        }
        /"plugins"[[:space:]]*:/       { in_plugins = 1; next }
        !in_plugins                    { next }
        /"name"[[:space:]]*:/          { name = strval($0); have = 1; next }
        have && /"source"[[:space:]]*:/ { print name "\t" strval($0); have = 0 }
    ' "$1"
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
    if ! grep -q '"plugins"[[:space:]]*:' "$MARKETPLACE"; then
        err "marketplace.json: no \"plugins\" array (invalid or malformed)"
        return
    fi

    # Collect plugin sources (leading "./" stripped) and validate each one is a
    # real plugin directory carrying a manifest. plugin_entries emits a
    # "name<TAB>source" line per object in the plugins array.
    local -a sources=()
    local name src
    while IFS=$'\t' read -r name src; do
        [ -n "$name" ] || continue
        src="${src#./}"
        sources+=("$src")
        [ -f "$SKILLS_SRC/$src/.claude-plugin/plugin.json" ] \
            || err "marketplace: plugin '$name' source '$src' has no .claude-plugin/plugin.json"
    done < <(plugin_entries "$MARKETPLACE")

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

# Every plugin/marketplace manifest version must match the VER file. Delegated
# to version.sh so the version logic lives in exactly one place.
if [ -x "$SKILLS_SRC/dev/version.sh" ]; then
    "$SKILLS_SRC/dev/version.sh" verify \
        || err "manifest versions drifted from VER (run ./dev/version.sh sync)"
else
    warn "skipping version-drift check (dev/version.sh missing or not executable)"
fi

# srd-standard.md must match its Confluence source per the divergence ledger.
# A warning, not an error: the source mirror exists only on machines with the
# vr checkout (elsewhere the script SKIPs and passes), and a red lint on those
# machines would train people to ignore it.
if [ -x "$SKILLS_SRC/dev/sync-srd-standard.sh" ]; then
    if ! sync_out="$("$SKILLS_SRC/dev/sync-srd-standard.sh" verify 2>&1)"; then
        warn "srd-standard.md drifted from its source (dev/sync-srd-standard.sh diff):"
        printf '%s\n' "$sync_out" | sed 's/^/       /'
    fi
fi

echo "----"
echo "$errors error(s), $warnings warning(s)."
[ "$errors" -eq 0 ]
