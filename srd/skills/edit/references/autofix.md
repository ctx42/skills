# autofix — bulk-applying a review's errata

The full procedure for `edit <srd> autofix`, read on demand when that mode
runs. Every other mode can ignore this file.

The errata class itself — what qualifies, and why a fix that needs prose to
describe is not errata — is defined in
[../../create/references/errata.md](../../create/references/errata.md).

## The run

Bulk-apply the errata `review` recorded — the fast path for surface fixes
before consistency work. Source of truth is the `## Errata` block of
`<srd>.review.md`: apply only what it lists and never re-scan the SRD for new
mechanical issues (that is `polish`). Errata is meaning-preserving and never
touches ids.

1. No review file, or an empty `## Errata` block: say so and stop.
2. Parse each open errata finding into its anchor and its fix, which the class
   in
   [../../create/references/errata.md](../../create/references/errata.md)
   states as an exact substitution — literal (`` `old` → `new` ``) or coded (a
   whitespace/glyph class plus a neighboring word, or a divider's heading plus
   `(missing)` → `---` or `---` → `(none)`; derive the canonical fix from the
   class). A finding with neither shape is not appliable: exclude it,
   report it as malformed, and tell the user to re-run `review <srd> errata`.
   A finding's number is the review file's global `#n`, kept when `review`
   moved it under `## Errata` — never its position in that block, so `#7` stays
   `#7` whether it sits first there or third.
3. Present the batch: every appliable finding (number, anchor, substitution).
   Appliable means well-shaped, not yet verified: say anchors are checked on
   apply, never that every finding will land.
   The user may name numbers to exclude; default is all.
4. One confirmation for the whole batch — `Yes` applies every included finding,
   `No` applies nothing. Not the loop.
5. On `Yes`, verify before every write: scope the search to the finding's
   anchor — the requirement entry, glossary entry, or heading it names, never
   the whole document — and count occurrences of `old`. An entry anchor reaches
   to the start of the next entry; a heading anchor reaches to the next heading
   of the same or a higher level, taking its subsections with it. Then:
   - exactly one → apply the substitution there.
   - zero → stale anchor; change nothing and report it.
   - more than one, and the finding did not name that many sites → ambiguous;
     change nothing and report it. Never guess.

   A whitespace or glyph finding has no literal `old` to count — `errata.md`
   forbids quoting whitespace, because the review file's own wrapping destroys
   the proof, so those findings carry a class plus a neighbouring word instead.
   Verify those by the class: find the neighbouring word inside the anchor,
   confirm the named defect is present beside it exactly once, and apply the
   canonical fix for that class. Absent or ambiguous behaves as above. A
   whitespace fix a sync restores is a no-op: report it, never re-apply it
   ([proposals.md](proposals.md#findings)).
   A missing-notice finding (`old` is `(missing)` and `new` the notice, per
   `errata.md`) has
   nothing to count in an anchor: count keyword notices in the whole SRD.
   Zero → insert `new` directly below the metadata block, after a TOC macro or
   block that follows the table; one or more → stale, as above.
   A GLO-4 link finding is verified by its term: it must occur unlinked in the
   anchor, nowhere earlier in the document, and linked nowhere later; then
   wrap that one occurrence in the link `glossary_terms` gives. Otherwise
   stale.
   A divider finding (`new` or `old` is `---`) is verified just above its
   heading, outside the heading's range (or at the document's end for
   `(end of document)`): blank lines aside, an insertion needs no `---` line
   there, a removal exactly one; insert or delete that one line, adding a blank
   line on any side that lacks one. Otherwise stale.
   A multi-site finding is verified per site and applies only where it
   matches; report each site that did not. Never substitute by whole-document
   search-and-replace; never widen beyond the quoted `old`.
6. Log every applied substitution in `<srd>.decisions.md` — one entry each,
   per [decision-log.md](decision-log.md). The batch path owes the log exactly
   what the loop owes it: this procedure covers finding and applying the
   fixes, not the whole of what the mode owes.
7. When anything landed, hand off to `review <srd> check #n…` scoped to exactly
   the applied errata numbers, so `review` moves them to `## Resolved` and
   leaves other findings untouched. Hand off by naming that exact command for
   the user to run: `edit` never invokes `review`, which owns the review file.
   Skip the hand-off if nothing landed.
8. Session end (`SKILL.md`) runs without its step 1 (surface-only fixes) and
   invokes no delegate in its step 2 (autofix attests no fact and captures no
   gap; a prior session's drafts were checked at session start). Its step 3
   manifest is owed like every mode's, and also names the findings handed to
   `check` — not what `check` then did with them, which happens after this run
   ends — and every finding skipped as stale, ambiguous, or malformed.
