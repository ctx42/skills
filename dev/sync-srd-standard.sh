#!/usr/bin/env bash
# Verifies srd/skills/create/references/srd-standard.md (the agent-optimized
# SRD rule set) against its source of truth: the Confluence page mirrored by
# cfsync in the private vr checkout. The copy is a deliberate derivative —
# trimmed and reworded for agent use — so this script does not regenerate it;
# it proves that every difference is one recorded in the divergence ledger
# (dev/srd-standard-sync.tsv) and reports exact per-unit drift otherwise.
#
# Transform spec (source -> copy), applied by the maintainer, verified here:
#   - frontmatter, metadata table, [[TOC]], intro note   -> dropped
#   - "# Introduction", "# Scope" (SC-*/OSC-*)           -> dropped (ledger)
#   - common-knowledge glossary terms                    -> dropped (ledger)
#   - "N>" cfsync indent markers in kept glossary terms  -> stripped
#   - RFC keyword notice                                 -> kept (ledgered reword)
#   - "**ID-n:**" rules                                  -> kept verbatim,
#     except rewords recorded as RULE: ledger entries
#   - <!-- adf:expand --> placeholders (content lives ONLY in Confluence)
#                                        -> examples transcribed by hand into
#                                           authoring-guide.md; inventory in
#                                           the ledger as EXPAND: entries
#   - <!-- adf:orderedList --> (Quality Bar, same frozen-node situation)
#                                        -> six items transcribed by hand
#
# Frozen-node edits never change the exported Markdown; the source's
# page_version (bumped by Confluence on every edit) is the only signal, so a
# version mismatch with the copy's provenance header is itself a drift.
#
# Modes:
#   verify        (default) exit 0 clean or source-unreachable, 1 on drift
#   diff          verify + print the normalized texts of each drifting unit
#   hash <unit>   print "src=<sha12> repo=<sha12>" for one unit, e.g.
#                 'RULE:STA-4', 'TERM:Markdown', 'NOTICE' — used to seed and
#                 refresh ledger entries
#
# Source path: $SRD_STANDARD_SRC, else the default vr-checkout path below.
# Unreachable source prints SKIP and exits 0 so other machines and CI stay
# green. This script only reads the source; it never writes outside the repo.
#
# No external dependencies (pure bash + coreutils; no jq).
set -euo pipefail
export LC_ALL=C

SKILLS_SRC="$(cd "$(dirname "$0")/.." && pwd)"
COPY="$SKILLS_SRC/srd/skills/create/references/srd-standard.md"
LEDGER="$SKILLS_SRC/dev/srd-standard-sync.tsv"
SRC="${SRD_STANDARD_SRC:-$HOME/ws/vr/docs/infraport/guidelines_for_software_requirements_documents.md}"

MODE="${1:-verify}"

drifts=0
drift() { echo "DRIFT  $1"; drifts=$((drifts + 1)); }

# First 12 hex chars of sha256 over stdin — plenty to distinguish rule texts,
# short enough to read in the ledger.
sha12() { sha256sum | cut -c1-12; }

# Rules as "ID<TAB>text", one line per "**ID-n:**" block: whitespace-collapsed,
# wrapped lines joined, terminated by the first blank line. adf placeholders
# are stripped first so a rule followed by an expand marker still ends on its
# own blank line. SC-*/OSC-* are the source's meta-scope, dropped from the
# copy wholesale, so they are excluded on both sides (full-id anchor — a bare
# ^SC prefix would also eat SCO-*).
extract_rules() {
    grep -v '<!-- adf:' "$1" | awk '
        /^\*\*[A-Z]+-[0-9]+[a-z]?:\*\*/ {
            if (id != "") print id "\t" text
            id = $1; gsub(/[*:]/, "", id)
            text = $0
            sub(/^\*\*[A-Z]+-[0-9]+[a-z]?:\*\*[[:space:]]*/, "", text)
            next
        }
        id != "" && /^$/ { print id "\t" text; id = ""; text = ""; next }
        id != "" {
            line = $0; sub(/^[[:space:]]+/, "", line)
            text = text " " line
        }
        END { if (id != "") print id "\t" text }
    ' | awk -F'\t' '$1 !~ /^(SC|OSC)-[0-9]+$/' | sort
}

# Glossary terms as "Term<TAB>definition" from the "# Glossary" section:
# cfsync "N>" indent markers stripped, blank lines dropped, wrapped lines
# joined, whitespace collapsed.
extract_terms() {
    awk '
        /^# Glossary$/ { g = 1; next }
        g && /^# /     { exit }
        !g             { next }
        /^## / {
            if (term != "") print term "\t" text
            term = $0; sub(/^## /, "", term); text = ""
            next
        }
        term == "" || /^$/ { next }
        {
            line = $0
            sub(/^[0-9]+>[[:space:]]*/, "", line)
            sub(/^[[:space:]]+/, "", line)
            text = (text == "" ? line : text " " line)
        }
        END { if (term != "") print term "\t" text }
    ' "$1" | sort
}

# The RFC keyword notice: the file's first blockquote, panel-type line
# ("[!INFO]") dropped, "> " prefixes stripped, joined to one line.
extract_notice() {
    awk '
        /^>/ {
            inq = 1
            line = $0; sub(/^>[[:space:]]?/, "", line)
            if (line ~ /^\[![A-Z]+\]$/) next
            text = (text == "" ? line : text " " line)
            next
        }
        inq { exit }
        END { print text }
    ' "$1"
}

# localIds of the source's adf:expand placeholders, one per line.
extract_expands() {
    grep -o 'adf:expand localId="[^"]*"' "$1" | cut -d'"' -f2 | sort || true
}

page_version_src() {
    awk '/^page_version:/ { gsub(/[^0-9]/, "", $2); print $2; exit }' "$SRC"
}

page_version_copy() {
    grep -o 'page_version [0-9]*' "$COPY" | awk '{ print $2; exit }'
}

declare -A L_SRC L_REPO
ledger_load() {
    [ -f "$LEDGER" ] || {
        echo "ERROR  ledger $LEDGER missing"
        exit 1
    }
    local unit src repo note
    while IFS=$'\t' read -r unit src repo note; do
        case "$unit" in '' | '#'*) continue ;; esac
        L_SRC["$unit"]="$src"
        L_REPO["$unit"]="$repo"
    done <"$LEDGER"
}

# Print a drifting unit's normalized texts (diff mode only).
show_texts() {
    local name="$1" st="$2" rt="$3"
    echo "------ $name"
    echo "source: ${st:-<absent>}" | fold -s -w 78
    echo "copy:   ${rt:-<absent>}" | fold -s -w 78
}

# check_unit NAME src_text repo_text — identical-and-present passes free;
# any other combination must match a ledger entry's recorded hashes.
check_unit() {
    local name="$1" st="$2" rt="$3" sh="-" rh="-"
    [ -n "$st" ] && [ "$st" = "$rt" ] && return 0
    [ -n "$st" ] && sh="$(printf '%s' "$st" | sha12)"
    [ -n "$rt" ] && rh="$(printf '%s' "$rt" | sha12)"
    if [ -z "${L_SRC[$name]+x}" ]; then
        if [ -z "$rt" ]; then
            drift "NEW: $name exists only in the source — add it to the copy or ledger it"
        elif [ -z "$st" ]; then
            drift "REPO-ONLY: $name is not in the source and not in the ledger"
        else
            drift "DIVERGES: $name differs and has no ledger entry (src $sh, repo $rh)"
        fi
        [ "$MODE" = diff ] && show_texts "$name" "$st" "$rt"
        return 0
    fi
    local ok=1
    [ "$sh" = "${L_SRC[$name]}" ] || {
        drift "SOURCE CHANGED: $name (src $sh, ledger ${L_SRC[$name]}) — re-apply the trim, refresh the ledger"
        ok=0
    }
    [ "$rh" = "${L_REPO[$name]}" ] || {
        drift "REPO EDITED: $name (repo $rh, ledger ${L_REPO[$name]}) — push upstream or restore, then refresh the ledger"
        ok=0
    }
    [ "$ok" = 1 ] || [ "$MODE" != diff ] || show_texts "$name" "$st" "$rt"
    return 0
}

# Text of one unit ("RULE:GLO-3", "TERM:Markdown", "NOTICE") in a file.
unit_text() {
    local f="$1" unit="$2"
    case "$unit" in
    RULE:*) extract_rules "$f" | awk -F'\t' -v id="${unit#RULE:}" '$1 == id { print $2 }' ;;
    TERM:*) extract_terms "$f" | awk -F'\t' -v t="${unit#TERM:}" '$1 == t { print $2 }' ;;
    NOTICE) extract_notice "$f" ;;
    *)
        echo "ERROR  unknown unit '$unit' (want RULE:<id>, TERM:<term>, NOTICE)" >&2
        exit 2
        ;;
    esac
}

hash_mode() {
    local unit="$1" st rt sh="-" rh="-"
    st="$(unit_text "$SRC" "$unit")"
    rt="$(unit_text "$COPY" "$unit")"
    [ -n "$st" ] && sh="$(printf '%s' "$st" | sha12)"
    [ -n "$rt" ] && rh="$(printf '%s' "$rt" | sha12)"
    printf 'src=%s\trepo=%s\n' "$sh" "$rh"
}

verify() {
    ledger_load

    # 1. page_version — the only signal for frozen-node edits (expands, the
    #    Quality Bar list), whose content never reaches the exported Markdown.
    local sv cv
    sv="$(page_version_src)"
    cv="$(page_version_copy)"
    if [ -z "$cv" ]; then
        drift "PROVENANCE: copy has no 'page_version N' header comment"
    elif [ "$sv" != "$cv" ]; then
        drift "STALE: source is at page_version $sv, copy synced at $cv — review frozen nodes in Confluence, then bump the header"
    fi

    # 2. top-level source sections — a brand-new one must be triaged into the
    #    transform (kept, trimmed, or dropped) before it can pass.
    local h
    while IFS= read -r h; do
        case "$h" in
        Introduction | Glossary | Scope | Requirements | "Quality Bar") ;;
        *) drift "NEW SECTION: '# $h' in the source — extend the transform and the ledger" ;;
        esac
    done < <(grep '^# ' "$SRC" | sed 's/^# //')

    # 3. rules, both directions.
    local src_rules repo_rules id st rt
    src_rules="$(extract_rules "$SRC")"
    repo_rules="$(extract_rules "$COPY")"
    while IFS= read -r id; do
        st="$(awk -F'\t' -v id="$id" '$1 == id { print $2 }' <<<"$src_rules")"
        rt="$(awk -F'\t' -v id="$id" '$1 == id { print $2 }' <<<"$repo_rules")"
        check_unit "RULE:$id" "$st" "$rt"
    done < <(printf '%s\n%s\n' "$src_rules" "$repo_rules" | cut -f1 | sort -u)

    # 4. glossary terms: kept terms must match; dropped ones need a
    #    "TERM:<term>  drop" ledger entry; copy-only terms are drift.
    local src_terms repo_terms term
    src_terms="$(extract_terms "$SRC")"
    repo_terms="$(extract_terms "$COPY")"
    while IFS= read -r term; do
        st="$(awk -F'\t' -v t="$term" '$1 == t { print $2 }' <<<"$src_terms")"
        rt="$(awk -F'\t' -v t="$term" '$1 == t { print $2 }' <<<"$repo_terms")"
        if [ "${L_SRC[TERM:$term]:-}" = "drop" ]; then
            [ -z "$rt" ] || drift "TERM:$term is ledgered as dropped but present in the copy"
            [ -n "$st" ] || drift "TERM:$term is ledgered as dropped but gone from the source — retire the entry"
            continue
        fi
        check_unit "TERM:$term" "$st" "$rt"
    done < <(printf '%s\n%s\n' "$src_terms" "$repo_terms" | cut -f1 | sort -u)

    # 5. the keyword notice — copied verbatim into every SRD via the template,
    #    so silent drift here is worse than anywhere.
    check_unit "NOTICE" "$(extract_notice "$SRC")" "$(extract_notice "$COPY")"

    # 6. expand inventory: every expand in the source maps to a transcribed
    #    example (authoring-guide.md); its content is invisible here, so only
    #    the id set is checkable.
    local eid
    while IFS= read -r eid; do
        [ -n "$eid" ] || continue
        [ -n "${L_SRC[EXPAND:$eid]+x}" ] ||
            drift "NEW EXPAND: $eid — read it in Confluence, transcribe into authoring-guide.md, add the ledger line"
    done < <(extract_expands "$SRC")
    local unit
    for unit in "${!L_SRC[@]}"; do
        case "$unit" in EXPAND:*) ;; *) continue ;; esac
        extract_expands "$SRC" | grep -qx "${unit#EXPAND:}" ||
            drift "EXPAND REMOVED: ${unit#EXPAND:} — check whether its authoring-guide section should go; retire the entry"
    done

    if [ "$drifts" -eq 0 ]; then
        echo "OK  srd-standard.md in sync with source (page_version $sv)"
    else
        echo "----"
        echo "$drifts drift(s). See CONTRIBUTING.md 'Syncing the SRD standard'."
    fi
    [ "$drifts" -eq 0 ]
}

[ -f "$SRC" ] || {
    echo "SKIP   source not available on this machine ($SRC)"
    exit 0
}

case "$MODE" in
verify | diff) verify ;;
hash)
    [ -n "${2:-}" ] || {
        echo "usage: $0 hash '<RULE:<id>|TERM:<term>|NOTICE>'" >&2
        exit 2
    }
    hash_mode "$2"
    ;;
*)
    echo "usage: $0 [verify|diff|hash <unit>]" >&2
    exit 2
    ;;
esac
