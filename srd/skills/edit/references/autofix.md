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
   whitespace/glyph class plus a neighboring word; derive the canonical fix
   from the class). A finding with neither shape is not appliable: exclude it,
   report it as malformed, and tell the user to re-run `review <srd> errata`.
3. Present the batch: every appliable finding (number, anchor, substitution).
   The user may name numbers to exclude; default is all.
4. One confirmation for the whole batch — `Yes` applies every included finding,
   `No` applies nothing. Not the loop.
5. On `Yes`, verify before every write: scope the search to the finding's
   anchor — the requirement entry, glossary entry, or heading it names, never
   the whole document — and count occurrences of `old`:
   - exactly one → apply the substitution there.
   - zero → stale anchor; change nothing and report it.
   - more than one, and the finding did not name that many sites → ambiguous;
     change nothing and report it. Never guess.

   A whitespace or glyph finding has no literal `old` to count — `errata.md`
   forbids quoting whitespace, because the review file's own wrapping destroys
   the proof, so those findings carry a class plus a neighbouring word instead.
   Verify those by the class: find the neighbouring word inside the anchor,
   confirm the named defect is present beside it exactly once, and apply the
   canonical fix for that class. Absent or ambiguous behaves as above.
   A multi-site finding is verified per site and applies only where it
   matches; report each site that did not. Never substitute by whole-document
   search-and-replace; never widen beyond the quoted `old`.
6. When anything landed, hand off to `review <srd> check #n…` scoped to exactly
   the applied errata numbers, so `review` moves them to `## Resolved` and
   leaves other findings untouched. Hand off by naming that exact command for
   the user to run: `edit` never invokes `review`, which owns the review file.
   Skip the hand-off if nothing landed.
7. The closing manifest names the findings handed to `check` — not what `check`
   then did with them, which happens after this run ends — and every finding
   skipped as stale, ambiguous, or malformed.
