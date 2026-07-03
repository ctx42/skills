#!/usr/bin/env bash
#
# glossary-terms.sh GLOSSARY_PATH
#
# Prints every term defined in a Markdown glossary, one per line, so the caller
# can detect which terms already exist and reuse them instead of defining them
# again.
#
# GLOSSARY_PATH may be either a single Markdown file or a directory. When it is a
# directory, every "*.md" file under it (recursively) is read, so a glossary can
# be one document or many spread across a folder tree.
#
# Each glossary entry is a Markdown "## " heading. A heading may carry an
# abbreviation in parentheses and/or an alias in brackets, e.g.
#   ## Application Programming Interface (API)
#   ## Identifier [Unique Identifier] (ID)
# For such a heading this emits the base term, the parenthetical abbreviation,
# and the bracketed alias as separate lines, since any of them may be referenced.
# Deeper headings (### …) are entry sub-parts, not terms, and are skipped.
#
# Dependencies: bash, grep, sed, sort (all standard). No packages to install.

set -euo pipefail

path=${1:-}
if [[ -z $path ]]; then
  echo "usage: glossary-terms.sh GLOSSARY_PATH" >&2
  exit 2
fi

# Collect the "## " headings from either a single file or a directory tree.
# `-h` drops filename prefixes; the pattern matches exactly two '#' then
# whitespace so deeper "### " sub-headings are excluded. A no-match grep (empty
# glossary) must not abort under `set -e`/`pipefail`, hence `|| true`.
if [[ -f $path ]]; then
  headings=$(grep -hE '^##[[:space:]]+' "$path" 2>/dev/null || true)
elif [[ -d $path ]]; then
  headings=$(grep -rhE '^##[[:space:]]+' --include='*.md' "$path" 2>/dev/null || true)
else
  echo "glossary-terms: not a file or directory: $path" >&2
  exit 1
fi

printf '%s\n' "$headings" \
| sed -E 's/^##[[:space:]]+//' \
| while IFS= read -r head; do
    # Parenthetical abbreviation(s): "(API)" -> API. A heading without one is
    # normal, so a no-match grep must not abort the loop under `set -e`.
    printf '%s\n' "$head" | grep -oE '\([^)]+\)' | sed -E 's/^\(|\)$//g' || true
    # Bracketed alias(es): "[Unique Identifier]" -> Unique Identifier
    printf '%s\n' "$head" | grep -oE '\[[^]]+\]' | sed -E 's/^\[|\]$//g' || true
    # Base term: drop the (...) and [...] groups, then trim surrounding spaces.
    # An `if` (not `&&`) keeps the loop's exit status 0 on an empty base, so a
    # glossary with no terms exits cleanly instead of tripping `pipefail`.
    base=$(printf '%s\n' "$head" \
      | sed -E 's/\([^)]*\)//g; s/\[[^]]*\]//g; s/^[[:space:]]+//; s/[[:space:]]+$//')
    if [[ -n $base ]]; then printf '%s\n' "$base"; fi
  done \
| sort -u
