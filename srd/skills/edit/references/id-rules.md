# Id rules

What the approval gate permits, and what any id change owes the user. Read
before proposing a change that touches a requirement, scope, or glossary id,
and before the first proposal of any kind on an approved SRD. `polish` on an
in-progress draft and `autofix` never need it.

On an approved SRD the gate governs content, not only ids. STA-4: adding,
removing, or changing a requirement needs the approving authority's agreement.
The user's `Y` is not that — it makes the edit the one they want, not one the
standard permits. So name STA-4 in the proposal and fold the ask into its one
question — `Y` here means the authority has agreed, not merely that the user
wants the edit — rather than trailing a second question after the choices.
Without that agreement, leave the edit marked for their ruling, unlanded. The
decision log records only applied edits and this skill writes no review file,
so an unlanded edit lives in the closing manifest or nowhere — list each with
its STA-4 ask. Removal is the sharp case, and it is written `**GR-6:** ~~the
requirement text~~`: the strikethrough covers the requirement text, never the
bold identifier, which STA-8 requires be kept — a struck id reads as retired
numbering rather than a retired rule. STA-8 keeps the id and strikes the text,
so "remove GR-4" is never a deletion (STA-7 keeps the number).
Meaning-preserving editorial change is STA-5 and needs none of this — `polish`
is that mode.

The gate then decides what may happen to requirement, scope, and glossary ids:

- In-progress: sub-number a split first — `GR-3` becoming `GR-3a`/`GR-3b` keeps
  every existing cross-reference working, which is why the authoring guide's
  own REQ-1 example does it. Renumbering the group is free here and is the
  right move when sub-numbering cannot express the change: an item crosses
  groups, or the numbering is already wrong (REQ-2/3/4 collisions and gaps).
  Removing a requirement deletes it outright; strikethrough is for approved
  SRDs only (STA-8). Update every cross-reference the change touches.
- Approved: existing ids are frozen. Additions only, via sub-numbering
  (`GR-1a`, `GR-1b`); never renumber or rename an existing id. A taken suffix
  moves down the alphabet — splitting `GR-3a` beside an existing `GR-3b` adds
  `GR-3c`. Never reuse a suffix, a struck-through one included: the id retires
  with its requirement. If a real fix
  cannot avoid touching an existing id, try add-only first; if that is
  impossible, present the conflict and the trade-off and leave it flagged
  unless the user explicitly approves the id change.

Whenever any id must change, state the change and get explicit approval as part
of the loop's confirmation. A renumbering pass excludes every comment block from
the substitution (comment text is verbatim history and may name an id that
never existed); verify afterwards that no comment line carries a new-scheme id.
