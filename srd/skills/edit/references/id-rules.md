# Id rules

What the approval gate permits, and what any id change owes the user. Read
before proposing a change that touches a requirement, scope, or glossary id,
and before the first proposal of any kind on a frozen or under-sign-off SRD.
`polish` on an in-progress draft and `autofix` never need it.

Under sign-off the gate governs content, not only ids: adding, removing, or
changing a requirement's meaning needs the sign-off the standard's lifecycle
rules name. The user's `Y` is not that — it makes the edit the one they want,
not one the standard permits. So cite that rule in the proposal and fold the
ask into its one question — `Y` here means the sign-off has been given, not
merely that the user wants the edit — rather than trailing a second question
after the choices. Without that sign-off, leave the edit marked for their
ruling, unlanded. When the standard also requires the change to be recorded
somewhere (a change-log section, say), that record is part of the edit. The
decision log records only applied edits and this skill writes no review file,
so an unlanded edit lives in the closing manifest or nowhere — list each with
its sign-off ask. Meaning-preserving editorial change follows the standard's
rule on wording fixes and needs none of this — `polish` is that mode.

Removal is the sharp case. Where the standard's rule on removed requirements
applies at the SRD's status, follow it exactly: keep what it says to keep (the
identifier, as a rule) and mark the text the way it sets, never the
identifier — a marked id reads as retired numbering rather than a retired
rule. So "remove ABC-4" is then never a deletion: the number stays. Where no
such rule applies, removal deletes the requirement outright.

The gate then decides what may happen to requirement, scope, and glossary ids:

- Renumbering allowed (the standard permits it at this status): sub-number a
  split first — `ABC-3` becoming `ABC-3a`/`ABC-3b` keeps every existing
  cross-reference working, which is why the authoring guide's own split
  example does it. Renumbering the group is free here and is the right move
  when sub-numbering cannot express the change: an item crosses groups, or the
  numbering is already wrong (collisions or gaps the identifier rules forbid).
  Update every cross-reference the change touches.
- Frozen: existing ids are frozen. Additions only, via sub-numbering
  (`ABC-1a`, `ABC-1b`); never renumber or rename an existing id. A taken
  suffix moves down the alphabet — splitting `ABC-3a` beside an existing
  `ABC-3b` adds `ABC-3c`. Never reuse a suffix, a removed one's included: the
  id retires with its requirement. If a real fix cannot avoid touching an
  existing id, try add-only first; if that is impossible, present the conflict
  and the trade-off and leave it flagged unless the user explicitly approves
  the id change.

Write every id in the identifier format the standard sets; the `ABC-n` forms
here are placeholders.

## Removal and comment blocks

Removing a requirement that carries a comment block names the comment in the
proposal and says `Y` settles it too; on apply, delete the `> [!comment]`
callout and its `[^…]` footnote anchor together.

## Any id change

Whenever any id must change, state the change and get explicit approval as part
of the loop's confirmation. A renumbering pass excludes every comment block from
the substitution (comment text is verbatim history and may name an id that
never existed); verify afterwards that no comment line carries a new-scheme id.
