# Finding and wording a change

What counts as a finding, and how a proposal words its fix. Read before the
interactive summary or the first proposal, whichever comes first; `autofix`
never needs it.

## Findings

- Requirements that read as overlapping are often independently testable (a
  disabled control vs a grayed one; a length cap vs its truncation format); a
  scope item covering one capability across many surfaces is atomic; a
  compound term whose parts are in the Company Glossary needs no entry.
- Never remove, or propose removing, an author's inline `(TBD: …)` reminder
  on a requirement, colored or not: it is the author's worklist, so recommend
  withdrawing a finding, REQ-7 included, that asks to drop it.
- Check every capitalized noun phrase that reads like a name against the
  glossaries and the requirements it summarizes; an undefined pseudo-name is a
  finding.
- Before merging two names for one thing, check they mean the same; when they
  differ in meaning, never pick one — put the question to the user
  ([Who would know](../../create/references/doc-corpus.md#who-would-know)).
- Before proposing, look for a prior ruling on what the change touches: grep
  `<srd>.decisions.md` and the knowledge base for the text it changes and for
  each entry id, matching the ranges and lists that span it ("GR-3 to GR-5",
  "GR-6, GR-8"), not the bare id alone; check every Out of Scope item against
  each surface the change adds, or its class. A ruling that keeps the text
  means leave it and recommend withdrawing the finding; one that excluded what
  the change adds is a conflict the proposal states.
- On an SRD another tool syncs, check the synced source after a round-trip
  before re-applying a whitespace fix: a fix the sync restores is a no-op —
  report it, never apply it again.

## Wording

- Keep each requirement standalone: never resolve a conflict by having one
  requirement cite others by id ("apply GR-6 through GR-10 only …"); put the
  condition in each rule, through a glossary term when it is long.
- When the user rewords a requirement to generalize it, confirm what the
  generalization means before proposing to remove siblings it seems to make
  redundant.
- Glossary definitions stay general: never name UI surfaces, labels, or where a
  term is shown — those change; they belong in UI requirements.
- Never propose a link from a requirement to end-user documentation; when a fix
  would need one, propose stating the rule or cutting the requirement instead.
- Write units of measure lowercase (minutes, hours, days), selectable values
  included; Title Case is for UI component names only.
- A bulk rename (a case change across defined terms, say) checks each term
  against the glossary that defines it first: a UI component name keeps its
  form.
- Never propose a casing-only change to make running text match a glossary
  heading, self-found or from a review, before checking the project's casing
  rules. Unless they require the glossary's casing in running text — silent
  or missing rules included — drop it; a review finding asking for it skips
  the loop with no proposal and goes in the manifest as declined.
- When a fix loosens an exhaustive rule ("exactly", "only") to admit an
  exception, keep its exclusion half and state the exception inside it; then
  re-validate what the rule no longer forbids.
- Check a heading rename against every other heading in the document, at any
  level or parent: a new name that duplicates one recreates the defect the
  rename fixes.
- Before carrying a fix to a sibling surface, check the sibling has the same
  shape (one item or a list); never collapse a per-item value into one value
  because a sibling was collapsed.
- Pad every Markdown table in a proposal to aligned columns, before-and-after
  tables included; check each row's width before sending.
- Proposals asked for to paste elsewhere carry only the before and after text:
  no rationale, headers, framing, or follow-up notes.

## Resolving a comment block

Only on the user's explicit ask: remove the `> [!comment]` callout and its
`[^…]` footnote reference from the requirement together, and log the removal.
A requirement removed with a comment on it follows
[id-rules.md](id-rules.md#removal-and-comment-blocks).

## Glossary

A run that reaches no term never calls `glossary_terms`. The procedure in
[../../create/references/srd-procedures.md](../../create/references/srd-procedures.md)
waits for the first thing that needs a term settled and lands before it: the
first proposal that introduces, renames or rests on a possibly company-defined
term, or in `interactive` the step-1 summary, which promises every issue found
and so owes GLO-3 too. A term put to the user against an unloaded term set is a
GLO-3 miss. Hold the set for the session.
