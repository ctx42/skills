#!/usr/bin/env bash
# Wrapper: the script ships in the craft:skill-eval skill; it runs on this repo.
r="$(cd "$(dirname "$0")/.." && pwd)"; SKILL_EVAL_ROOT="$r" exec "$r/craft/skills/skill-eval/scripts/eval-changed.sh" "$@"
