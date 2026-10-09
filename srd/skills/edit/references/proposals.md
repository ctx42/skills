# Finding and wording a change

What counts as a finding, and how a proposal words its fix. Read before the
interactive summary or the first proposal, whichever comes first; `autofix`
never needs it.

## Findings

- Requirements that read as overlapping are often independently testable (a
  disabled control vs a grayed one; a length cap vs its truncation format); a
  scope item covering one capability across many surfaces is atomic; a
  compound term whose parts are in the Company Glossary needs no entry.
- Check every capitalized noun phrase that reads like a name against the
  glossaries and the requirements it summarizes; an undefined pseudo-name is a
  finding.
- Before merging two names for one thing, check they mean the same; when they
  differ in meaning, never pick one — put the question to the user
  ([Who would know](../../create/references/doc-corpus.md#who-would-know)).
- Before proposing a fix, grep `<srd>.decisions.md` and the knowledge base for
  the text it changes: a prior ruling that keeps the text means leave it, and
  recommend withdrawing the finding.

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
- When a fix loosens an exhaustive rule ("exactly", "only") to admit an
  exception, keep its exclusion half and state the exception inside it; then
  re-validate what the rule no longer forbids.
- Pad every Markdown table in a proposal to aligned columns, before-and-after
  tables included; check each row's width before sending.

## Resolving a comment block

Only on the user's explicit ask: remove the `> [!comment]` callout and its
`[^…]` footnote reference from the requirement together, and log the removal.
A requirement removed with a comment on it follows
[id-rules.md](id-rules.md#removal-and-comment-blocks).
