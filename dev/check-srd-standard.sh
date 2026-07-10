#!/usr/bin/env bash
# Passive drift tripwire for srd/skills/create/references/srd-standard.md.
#
# srd-standard.md is generated from a Confluence page (id 1949564932, mirrored
# by cfsync into the private vr checkout). Regeneration is the `srd-sync` skill
# (LLM-driven); this script does NOT sync. It compares the source's page_version
# to the version recorded in the copy's own provenance banner (the sole record
# of what the copy was generated from — there is no separate state file), so
# lint-skills.sh can flag drift without anyone remembering to check.
#
# A single number is compared — no Markdown parsing — so this stays robust as
# the page's wording and structure change. Source unreachable -> SKIP, exit 0
# (machines without the vr checkout, and CI, stay green). Reads only; no writes.
set -euo pipefail
export LC_ALL=C

SKILLS_SRC="$(cd "$(dirname "$0")/.." && pwd)"
COPY="$SKILLS_SRC/srd/skills/create/references/srd-standard.md"
SRC="${SRD_STANDARD_SRC:-$HOME/ws/vr/docs/infraport/guidelines_for_software_requirements_documents.md}"

[ -f "$SRC" ] || { echo "SKIP   SRD source not on this machine ($SRC)"; exit 0; }

# Digits of the source frontmatter's page_version. Split on ':' then strip the
# value side to digits, so `page_version: 16` and `page_version:16` both parse.
src_ver="$(awk -F: '/^page_version:/ { v = $2; gsub(/[^0-9]/, "", v); print v; exit }' "$SRC")"
if [ -z "$src_ver" ]; then
    echo "ERROR  cannot parse page_version from $SRC"
    exit 1
fi

# The copy's provenance banner carries "page_version NN".
copy_ver="$([ -f "$COPY" ] && grep -oE 'page_version [0-9]+' "$COPY" | head -1 | tr -dc '0-9' || true)"

if [ -z "$copy_ver" ]; then
    echo "DRIFT  srd-standard.md has no page_version provenance — run the srd-sync skill to (re)generate it (source page_version $src_ver)"
    exit 1
elif [ "$src_ver" != "$copy_ver" ]; then
    echo "DRIFT  SRD source at page_version $src_ver, srd-standard.md generated from $copy_ver"
    echo "       run the srd-sync skill to regenerate (also re-check frozen nodes: Quality Bar, Bad→Good examples)"
    exit 1
fi
echo "OK  srd-standard.md current with source (page_version $src_ver)"
