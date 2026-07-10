#!/usr/bin/env bash
# Applies the closed set of plugin-only substitutions to srd-standard content
# read on stdin, printing the result. Called by the srd-sync skill (step 6),
# which pipes its assembled pre-substitution candidate through this so an LLM
# never performs the exact string replacement.
#
# Contract: for each rule, assert its source phrase occurs exactly once, then
# swap it. A count other than 1 means the phrase was reworded (or duplicated)
# upstream — the script exits 1 naming the rule, so srd-sync stops instead of
# passing source wording through silently; fix the rule here, never accept the
# new wording. (The RFC keyword notice and the REQ-7 aside are handled elsewhere,
# not here: the notice is header frame, the aside is a skill content trim.)
#
# "|" is the sed delimiter (absent from every pattern); regex metacharacters in
# the sed patterns are escaped. No external dependencies (bash + coreutils).
set -euo pipefail
export LC_ALL=C

# Buffer stdin so each phrase can be counted before the swap runs.
buf="$(mktemp)"
trap 'rm -f "$buf"' EXIT
cat >"$buf"

# Assert a literal phrase occurs exactly once in the buffered input.
assert_one() {
    local pat="$1" n
    # `|| true`: grep exits 1 on zero matches, which set -e would treat as fatal
    # before the count check runs — rescue it so 0 is reported as "matched 0".
    n="$(grep -Fo -- "$pat" "$buf" | wc -l)" || true
    [ "$n" -eq 1 ] || {
        echo "ERROR  substitution '$pat' matched $n times (want 1) — update dev/srd-subst.sh" >&2
        exit 1
    }
}

assert_one 'the Company Glossary'
assert_one '[company glossary](glossary/main_glossary.md)'
assert_one '[Quality Bar](guidelines_for_software_requirements_documents.md#Quality-Bar.1)'
assert_one 'the Technology Group'

sed \
    -e 's|the Company Glossary|the shared glossary|g' \
    -e 's|\[company glossary\](glossary/main_glossary\.md)|shared glossary|g' \
    -e 's|\[Quality Bar\](guidelines_for_software_requirements_documents\.md#Quality-Bar\.1)|Quality Bar|g' \
    -e 's|the Technology Group|the approving authority|g' \
    "$buf"
