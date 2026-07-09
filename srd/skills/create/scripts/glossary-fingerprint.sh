#!/usr/bin/env bash
#
# glossary-fingerprint.sh GLOSSARY_PATH
#
# Prints a single deterministic content hash of a Markdown glossary, so the
# caller can tell whether the glossary changed since it last built its digest
# and rebuild that (expensive, model-synthesized) digest only when the hash
# actually differs.
#
# GLOSSARY_PATH may be a single Markdown file or a directory. For a directory,
# every "*.md" file under it (recursively) contributes, so adding, removing, or
# editing any file changes the hash. The hash combines each file's path
# (relative to GLOSSARY_PATH) with a hash of its contents, sorted, so the result
# is independent of filesystem traversal order, mtimes, and the absolute
# location on disk — the same docs yield the same hash on any machine or
# checkout, and a rename counts as a change.
#
# Output: the hash on stdout and nothing else, exit 0. An empty glossary (no
# "*.md" files) yields the stable hash of the empty string. A path that is
# neither a file nor a directory prints nothing and exits 1, so the caller can
# fall back to an empty glossary and define every term locally.
#
# Dependencies: bash, find, sort, sha256sum, cut (all standard). No packages to
# install.

set -euo pipefail

path=${1:-}
if [[ -z $path ]]; then
  echo "usage: glossary-fingerprint.sh GLOSSARY_PATH" >&2
  exit 2
fi

# Emit "<content-hash>  <relpath>" for one file. The relpath is passed in (not
# derived here) so it feeds the final hash too — a rename with unchanged bytes
# still shifts the fingerprint.
hash_one() {
  local file=$1 rel=$2
  printf '%s  %s\n' "$(sha256sum "$file" | cut -d' ' -f1)" "$rel"
}

if [[ -f $path ]]; then
  manifest=$(hash_one "$path" "$(basename "$path")")
elif [[ -d $path ]]; then
  # Build the manifest from inside $path (in a subshell, so the caller's cwd is
  # untouched) to make relpaths location-independent. -print0 / sort -z keep
  # filenames with spaces or newlines intact; sort makes the order deterministic
  # regardless of how the filesystem returns entries. Functions are inherited by
  # the command-substitution subshell, so hash_one is in scope.
  manifest=$(
    cd "$path"
    while IFS= read -r -d '' file; do
      hash_one "$file" "${file#./}"
    done < <(find . -type f -name '*.md' -print0 | sort -z)
  )
else
  echo "glossary-fingerprint: not a file or directory: $path" >&2
  exit 1
fi

# Fold the per-file manifest into one hash. An empty manifest hashes the empty
# string (a stable, non-empty marker), so an empty glossary is still comparable.
printf '%s' "$manifest" | sha256sum | cut -d' ' -f1
