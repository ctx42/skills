#!/usr/bin/env bash
# PreToolUse guard for skill edits.
#
# When a Write/Edit targets a file under any `.../skills/<name>/` directory, this
# injects a reminder to hold the change to the skill-smith authoring standard.
# Soft nudge only: it never blocks the edit. Requirements themselves live in
# craft/skills/skill-smith/standards.md — this hook only points at them so the
# rules stay in one place.
#
# No jq: the tool-call JSON arrives on stdin; we pull file_path with grep/sed.
set -eu

input=$(cat)

# Extract the target path (Write and Edit both use "file_path").
path=$(printf '%s' "$input" \
  | grep -oE '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' \
  | head -n1 \
  | sed -E 's/.*"file_path"[[:space:]]*:[[:space:]]*"([^"]*)".*/\1/') || true

# A file is a skill file if it is a SKILL.md, or a sibling of one (README,
# standards.md, …), or a bundled file one level down (references/, scripts/,
# assets/). Keying off SKILL.md — not the path string — avoids false positives
# from this repo itself being named "skills". Non-skill edits pass untouched.
[ -n "${path:-}" ] || exit 0
dir=$(dirname "$path")
base=$(basename "$path")
if [ "$base" != "SKILL.md" ] \
  && [ ! -f "$dir/SKILL.md" ] \
  && [ ! -f "$dir/../SKILL.md" ]; then
  exit 0
fi

# additionalContext is added to the model's context before the edit runs.
cat <<'JSON'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "additionalContext": "This file lives in a skill. Before writing, hold the change to the skill-smith authoring standard (craft/skills/skill-smith/standards.md) — especially the Token performance, Body: conciseness, and Output discipline rules: the description and SKILL.md body are always-loaded token cost, so cut anything that does not raise the skill's success rate, push on-demand detail into references, and keep runtime output terse. For a new skill or a structural change (rename, new files, catalog updates), run the skill-smith skill in create/improve mode rather than editing ad hoc."
  }
}
JSON
