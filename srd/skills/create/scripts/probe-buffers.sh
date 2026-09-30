#!/usr/bin/env bash
#
# probe-buffers.sh [SRD_PATH] [SRD_ID]
#
# Reports which SRD delegate buffers hold pending records for one SRD, so a
# skill can invoke `srd:report-doc-gap` and `srd:kb` only when there is
# something to drain. Both delegates buffer to disk and both hold that a file
# exists only while records are pending, so this probe answers exactly what
# invoking the two skills answers — at a fraction of the cost, since an absent
# buffer is the usual case and loading a skill to learn it is the single
# largest waste at session start.
#
# SRD_PATH is the SRD's file path (need not exist yet); with none, no per-SRD
# buffer can be keyed and only the kb-root line is meaningful. SRD_ID is the id the
# document carries, when it carries one; both buffers are keyed by id once
# assigned and by path before that, and a buffer opened before assignment may
# still be path-keyed, so both keys are probed whenever an id is given. The SRD
# skills pass none: the SRD template has no id field, so documents in this
# project are path-keyed throughout, and the argument is for a caller holding an
# id from elsewhere. The
# path key is "path-" plus the first 12 hex characters of the SHA-256 of the
# absolute path — the derivation both delegates specify; deriving it any other
# way probes a file neither of them wrote.
#
# Output: one "<name>: <state> [path]" line per buffer on stdout, exit 0.
# State is "pending" (invoke that delegate to drain it) or "none" (do not).
# The kb-root line reports whether `srd:kb` already knows where the knowledge
# base lives: "missing" means it will ask, which belongs at the first captured
# fact, not in the closing report.
#
# Dependencies: bash, sha256sum (or shasum), cut (all standard).

set -euo pipefail

srd_path=${1:-}
srd_id=${2:-}

mem="${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/srd"

sha256() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum
  else
    shasum -a 256
  fi
}

# Absolute without requiring the file to exist: a new SRD is keyed before it is
# written, and a relative key derived from two working directories would split
# one SRD's buffer in two. An existing directory is resolved by cd so the key
# survives being reached by different relative routes; a directory that does
# not exist yet is anchored to $PWD instead, never left relative.
abs_path() {
  local p=$1 dir base
  dir=$(dirname -- "$p")
  base=$(basename -- "$p")
  if [[ -d $dir ]]; then
    dir=$(cd "$dir" && pwd)
  else
    [[ $dir != /* ]] && dir="$PWD/$dir"
    dir=$(normalize "$dir")
  fi
  printf '%s/%s\n' "$dir" "$base"
}

# Collapse "", ".", and ".." segments lexically. Needed only for a directory
# that does not exist yet (cd does it for one that does), and lexical for the
# same reason: there is nothing on disk to walk.
normalize() {
  local seg out=()
  local IFS=/
  for seg in $1; do
    case $seg in
      '' | .) ;;
      ..) [[ ${#out[@]} -gt 0 ]] && unset 'out[-1]' ;;
      *) out+=("$seg") ;;
    esac
  done
  printf '/%s' ${out+"${out[@]}"}
  printf '\n'
}

# With no SRD yet — a `create` interview before the file is named, or a mode
# with no SRD at all — there is no per-SRD buffer to key, so only kb-root is
# reported. Refusing to run would deny the caller the one signal it can still
# use.
if [[ -n $srd_path ]]; then
  path_key="path-$(printf '%s' "$(abs_path "$srd_path")" | sha256 | cut -c1-12)"
else
  path_key=""
fi

report() {
  local name=$1 file=$2
  if [[ -f $file ]]; then
    printf '%s: pending %s\n' "$name" "$file"
  else
    printf '%s: none\n' "$name"
  fi
}

if [[ -n $path_key ]]; then
  printf 'key-path: %s\n' "$path_key"
else
  printf 'key-path: none (no SRD path given)\n'
fi
if [[ -n $srd_id ]]; then
  printf 'key-id: %s\n' "$srd_id"
fi

for store in docgaps kb; do
  hit=""
  if [[ -n $srd_id && -f "$mem/$store/$srd_id.json" ]]; then
    hit="$mem/$store/$srd_id.json"
  elif [[ -n $path_key && -f "$mem/$store/$path_key.json" ]]; then
    hit="$mem/$store/$path_key.json"
  fi
  report "$store" "${hit:-/nonexistent}"
done

if [[ -s "$mem/kb-root" ]]; then
  printf 'kb-root: %s\n' "$(cat "$mem/kb-root")"
else
  printf 'kb-root: missing\n'
fi
