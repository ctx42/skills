#!/usr/bin/env bash
# Prints each skill's always-loaded token surface so regressions show up in
# review: description chars (paid every session, for every skill) and the
# SKILL.md body word count with a rough token estimate (paid on every
# trigger; 1 token ~ 0.75 words). Reference files are listed with their word
# counts but not totalled — they are on-demand and cost nothing until read.
#
# No external dependencies (pure bash + coreutils; no jq).
set -euo pipefail
shopt -s nullglob

SKILLS_SRC="$(cd "$(dirname "$0")/.." && pwd)"

# Print the YAML frontmatter block (between the first two --- lines) of a file.
frontmatter() {
    awk 'NR==1 && $0=="---"{f=1; next} f && $0=="---"{exit} f' "$1"
}

# Join a plain or folded description scalar into one line.
description() {
    awk '
        /^description:/ {
            d = 1
            sub(/^description:[[:space:]]*[>|]?[[:space:]]*/, "")
            if (length($0)) printf "%s ", $0
            next
        }
        d && /^[a-zA-Z_-]+:/ { d = 0 }
        d { sub(/^[[:space:]]+/, ""); printf "%s ", $0 }
    ' <<<"$(frontmatter "$1")"
}

# Words / estimated tokens for a file. 4/3 words per token is a coarse but
# stable estimate — good enough to spot growth between two runs.
tokens() { echo $(($1 * 4 / 3)); }

total_desc=0
total_body=0

printf '%-22s %6s %7s %8s\n' "skill" "desc" "body-w" "~body-t"
printf '%-22s %6s %7s %8s\n' "-----" "----" "------" "-------"

while IFS= read -r skill_md; do
    dir="$(dirname "$skill_md")"
    name="$(basename "$(dirname "$dir")"):$(basename "$dir")"
    [ "$(basename "$(dirname "$dir")")" = "skills" ] \
        && name="$(basename "$(dirname "$(dirname "$dir")")"):$(basename "$dir")"

    desc="$(description "$skill_md")"
    desc="${desc% }"
    words="$(wc -w <"$skill_md")"

    printf '%-22s %6d %7d %8d\n' "$name" "${#desc}" "$words" "$(tokens "$words")"
    total_desc=$((total_desc + ${#desc}))
    total_body=$((total_body + words))
done < <(find "$SKILLS_SRC" -path "$SKILLS_SRC/tmp" -prune -o -name SKILL.md -print | sort)

printf '%-22s %6s %7s %8s\n' "-----" "----" "------" "-------"
printf '%-22s %6d %7d %8d\n' "total" "$total_desc" "$total_body" \
    "$(tokens "$total_body")"
echo
echo "On-demand references (loaded only when a workflow step reads them):"
while IFS= read -r f; do
    printf '  %6d words  %s\n' "$(wc -w <"$f")" "${f#"$SKILLS_SRC"/}"
done < <(find "$SKILLS_SRC" -path "$SKILLS_SRC/tmp" -prune -o \
    \( -path '*/references/*.md' -o -path '*/assets/*.md' \) -print | sort)
