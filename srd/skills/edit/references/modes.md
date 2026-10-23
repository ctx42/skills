# Mode procedures

The procedures for `walk`, `feedback`, `polish`, `targeted`, and the start
points (an interactive start line or id, a feedback `#n`). Read when the run is
one of those; `load` is in `SKILL.md`, and `autofix` is in
[autofix.md](autofix.md).

## interactive (`walk`)

1. Front-load a grouped issue summary — every issue found, grouped by document
   section (Metadata, Introduction, Glossary, Scope, Requirements), each citing
   its rule id. Edit nothing yet; the first proposal may follow in the same
   turn.
2. Walk entry by entry in document order — each requirement (`PFX-n`), glossary
   term, scope item — running the loop for every fix the user approves; Scope
   goes last, after Requirements, since it derives from them. Move on only on
   `YN` or an explicit ask, and never before the current entry is resolved or
   skipped. An entry with no finding resolves on sight: say so and move on —
   nothing was proposed, so no key is owed.

## interactive start point (path + line or id)

Resolve the line to the entry or paragraph at or nearest it, or the id to its
entry — an id the SRD lacks gets one line saying so, and the run stops — skip
step 1, and begin step 2 there, continuing to the end; Scope entries at or
after the start still go last, those before it are skipped. The walk is still
one entry at a time and still never looks ahead — step 1's summary is what
would have told you which later entry has a finding, and skipping it means
learning that entry by entry, never by scanning forward.

## feedback

Apply findings from a review; the review file stays untouched regardless of
outcome.

1. Input is a `<srd>.review.md` path or feedback pasted inline (email, ticket,
   chat); parse the findings from either.
2. Work findings in two passes: every section but Scope, then Scope, which
   derives from the settled requirements (SCO-2/3). Within each pass, severity
   order — blocker → major → minor — using the review's tags and numbers; judge
   untagged pasted feedback from the rule.
3. Run the loop per finding; reference findings by number in the closing
   manifest.
4. Close by pointing the user to `review <srd> check` to reclassify what
   landed.

## feedback start point (path + `#n`)

Requires an existing `<srd>.review.md` (the SRD's path with `.md` replaced:
`specs/login.md` → `specs/login.review.md`); if absent, say so and stop — one
or two lines naming the missing file, nothing more. No approval-gate line,
draft check, manifest, or way in — not even "run `srd:review` first": those
report a run that happened, and this one did not. Enter at finding `#n`
instead of the passes and severity order; after each finding, default to the
next by number or jump to any number the user names. The explicit `#n` sets the
order for the rest of the run: walk ascending from `n` to the end, then come
back for the lowest still open; a jump re-anchors the walk the same way.

## polish

Mechanical-only cleanup through the loop, confirming each change, in document
order with no summary first; metadata gaps go to the closing manifest, not the
walk. Scope: British → US spelling, identifier format/order (REQ-2/3/4,
subject to the approval gate), keyword capitalization (LANG-4), valid
Markdown, requirement-group dividers (authoring guide), stray example/note
text (REQ-7), spacing and punctuation. Never rewrite requirement meaning,
restructure, or cut a requirement.

## targeted

Edit one entry the user points to by requirement id with the change wanted
(`GR-3a name the lockout minutes`), glossary term, quoted text, or free
description ("the login timeout rule"). A bare requirement or scope id is an
interactive start point instead; a bare glossary term stays targeted.

1. Locate the target; for quoted text or a description, confirm the match
   before editing, inside the proposal: it is the loop's one question, so say
   the match outright ("taking 'fast' to be GR-4"), and `E` corrects it. With
   nothing to fix on it, say so and ask what they want changed rather than
   manufacturing a finding.
2. Run the loop on that entry. The change the user named is still only a
   proposal: write it out in full with its keys and end the turn there —
   naming a change is not approving its wording, so nothing is applied before
   the key that answers it. Its resolution ends the run (Session end) — except
   under `load`, where the session stays open until the user says they are
   done.
3. Report the re-validation result explicitly: whether the edit introduced any
   inconsistency in the entry or its cross-refs.
