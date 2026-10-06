# Mode procedures

The procedures for `polish`, `targeted`, and an interactive start line. Read
when the run is one of those; the default interactive walk and `feedback` are
in `SKILL.md`, and `autofix` is in [autofix.md](autofix.md).

## interactive start point (path + line)

Resolve the line to the entry or paragraph at or nearest it, skip step 1, and
begin step 2 there, continuing to the end; Scope entries at or after the start
still go last, those before it are skipped. The walk is still one entry at a
time and still never looks ahead — step 1's summary is what would have told
you which later entry has a finding, and skipping it means learning that entry
by entry, never by scanning forward.

## polish

Mechanical-only cleanup through the loop, confirming each change, in document
order with no summary first; metadata gaps go to the closing manifest, not the
walk. Scope: British → US spelling, identifier format/order (REQ-2/3/4,
subject to the approval gate), keyword capitalization (LANG-4), valid
Markdown, requirement-group dividers (authoring guide), stray example/note
text (REQ-7), spacing and punctuation. Never rewrite requirement meaning,
restructure, or cut a requirement.

## targeted

Edit one entry the user points to by requirement id (`GR-3a`), quoted text, or
free description ("the login timeout rule").

1. Locate the target; for quoted text or a description, confirm the match
   before editing, inside the proposal: it is the loop's one question, so say
   the match outright ("taking 'fast' to be GR-4"), and `E` corrects it. With
   nothing to fix on it, say so and ask what they want changed rather than
   manufacturing a finding.
2. Run the loop on that entry; its resolution ends the run (Session end).
3. Report the re-validation result explicitly: whether the edit introduced any
   inconsistency in the entry or its cross-refs.
