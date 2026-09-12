#!/usr/bin/env bash
# Applies the closed set of plugin-only substitutions to srd-standard content
# read on stdin, printing the result. Called by the srd-sync skill (step 6),
# which pipes its assembled pre-substitution candidate through this so an LLM
# never performs the exact string replacement.
#
# Contract: for each rule, assert its source phrase is present, then swap every
# occurrence. Zero matches means the phrase was reworded upstream — the script
# exits 1 naming the rule, so srd-sync stops instead of passing source wording
# through silently; fix the rule here, never accept the new wording. Two or
# more is not an error: a phrase legitimately appears in more than one rule
# (the glossary link is cited by GLO-3 and STR-10 both), and the swap is
# global, so every copy is rewritten.
#
# Each rule also guards against matching inside a longer phrase, because these
# are substring matches: "the Technology Group" sits inside "the Technology
# Group Lead", and swapping there yields "the approving authority Lead". (The RFC keyword notice and the REQ-7 aside are handled elsewhere,
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

# Assert a literal phrase is present in the buffered input. Reports the count so
# a sync log shows how many copies were rewritten.
assert_present() {
    local pat="$1" n
    # `|| true`: grep exits 1 on zero matches, which set -e would treat as fatal
    # before the count check runs — rescue it so 0 is reported as "matched 0".
    n="$(grep -Fo -- "$pat" "$buf" | wc -l)" || true
    [ "$n" -ge 1 ] || {
        echo "ERROR  substitution '$pat' matched 0 times — reworded upstream; update dev/srd-subst.sh" >&2
        exit 1
    }
    echo "subst  '$pat' x$n" >&2
}

# Refuse to swap a phrase that only occurs inside a longer one, which a
# substring match cannot tell apart.
assert_not_inside() {
    local pat="$1" hit
    hit="$(grep -Eo -- "$pat" "$buf" | head -1)" || true
    [ -z "$hit" ] || {
        echo "ERROR  '$hit' extends the phrase being substituted — update dev/srd-subst.sh" >&2
        exit 1
    }
}

assert_present '[company glossary](glossary/main_glossary.md)'
assert_present '[Quality Bar](guidelines_for_software_requirements_documents.md#Quality-Bar.1)'
assert_present 'the Technology Group'
assert_not_inside 'the Technology Group [A-Z][a-zA-Z]+'

sed \
    -e 's|\[company glossary\](glossary/main_glossary\.md)|Company Glossary|g' \
    -e 's|\[Quality Bar\](guidelines_for_software_requirements_documents\.md#Quality-Bar\.1)|Quality Bar|g' \
    -e 's|the Technology Group|the approving authority|g' \
    "$buf"
