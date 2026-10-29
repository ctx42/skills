# SRD Authoring Guide — House Extensions and Defect Classes

Practical guidance that extends the SRD standard, read live through the server
(`project-config.md`). The standard's rules are normative; the items here are
this project's additions plus worked examples that help the agent draft well and
recognize defects during the self-check. Nothing here names a rule, field,
status value, or section of any one standard: where an item needs one, it says
what to look for in the fetched standard.

**These examples never go into an SRD.** Every `Bad`/`Good` pair below is
authoring guidance only. A real SRD carries the rule and nothing more.

## Contents

- House additions to the rules
- Consistency pass
- Defect classes (Bad → Good)
- Good atomic requirements

## House additions to the rules

The fetched standard outranks this list: where it states a rule a house
addition also states, apply its wording and cite its identifier as the
standard writes it (`SRD:<id>`, e.g. `SRD:ABC-1`), never `SRD:house`; the house
addition supplies only what the standard leaves out, and every `SRD:house`
below applies only when the standard has no such rule. Casing rules the
standard states count as the project's casing rules.

- Write SRDs in US English: `color`, `behavior`, `standardize`,
  `analyze`, `center` — not `colour`, `behaviour`, `standardise`. The self-check
  flags British spellings. (This governs the SRD artifact only.)
- Sub-numbering is allowed where the standard's numbering rule permits it:
  within a group, tightly-coupled requirements MAY take a one-letter suffix —
  `ABC-1a`, `ABC-1b`, in the identifier format the standard sets — when it aids
  readability. Keep it shallow; do not nest deeper than one letter. Plain
  `ABC-1`, `ABC-2` remains the default; reach for suffixes only when several
  rules form one tight cluster.
- Introduction "will not do": when the standard asks the introduction to say
  what the system will not do, a purpose plus a high-level account of what the
  system *will* do satisfies it whenever the out-of-scope list is present —
  that list carries the exclusions, not restated in the intro. Do not raise an
  intro finding for a missing explicit "will not do" then.
- Terminology consistency: use one term per concept throughout. Do not mix
  synonyms for the same thing (e.g. `hot-fire` / `static fire` /
  `test firing`); pick one and define it once. This is the one definition of
  terminology drift — the consistency pass and the defect class below both
  spot it, neither redefines it, and a finding against it cites the
  standard's one-term rule, else this house addition (`SRD:house`).
  Qualify overloaded terms ("slot", "window", "status", "channel") with what
  they belong to ("a launch slot's `status` field"); terseness never excuses
  a term that resolves differently in another document.
- A local terms section is conditional when the standard ties it to terms that
  need a definition: never require one when nothing needs defining. Proper
  names (product or module names, external tools, vehicle models) are not
  concepts and are not undefined-term gaps.
- Plain headings: never bold a heading (`### **X**`); de-bold existing ones.
- Requirement-group dividers: under the requirements section, put a `---` line
  before every group heading and one after the last group, a blank line on each
  side (else the line above turns into a heading); use `---` nowhere else in
  the body. A missing divider is a finding.
- Link, do not restate: when a requirement would repeat rules an authoritative
  platform document defines, link that document and state only the SRD-level
  constraint.
- Plain language: short sentences, everyday verbs, at most one condition
  clause; never stack nested qualifiers. Aim for wording a B2 English reader
  gets on one pass, and reach for it when a requirement is genuinely dense —
  but a clear requirement is not a defect because a simpler phrasing exists.
  The linked platform document carries the precision.
- Grade a group code only by the strength the standard gives its code rule:
  under a SHOULD, a code outside the preferred form is a deviation, not a
  defect; under a MUST, only a code that breaks it. Beyond that, raise a code
  finding only when the code is unclear or collides with another group's.
- A vehicle or engine model named in a requirement (`Ember`, `Anvil`) is the
  correct scope when the UI surface or feature exists only for those models;
  never propose generalizing it away.
- No catch-all requirement ("features not addressed behave identically"): an
  SRD specifies only what changes; unspecified areas are unchanged by default,
  and such a rule is weakly verifiable (the standard's checkability and
  open-ended-wording rules).
- Narrowing is layering, not contradiction: an SRD that offers less than a
  platform document says the system can do is not a corpus gap and the
  platform document is not wrong. A role or setting that restores the full
  capability is the tell that both statements hold.
- The standard's letter codes are not reserved: its own rule identifiers must
  never be pasted into an SRD, but a requirement group may use the same
  letters. Never raise a code "collision" with the standard as a finding.
- Template macros are opaque house syntax: a `[[TOC]]` macro, a status macro
  (`[[!<value>|…]]`), and the `[!INFO]` callout header are deliberate and valid
  Obsidian Markdown — keep them verbatim; never "fix" them to GitHub forms. A
  TOC macro expands to a generated table of contents, not to document content,
  so it never breaks a rule about what follows what: a notice or section the
  standard places directly after the metadata still comes first when only the
  macro sits between them. Never raise that finding, and never move the macro
  to answer it.
- Scope items stand alone: an in-scope or out-of-scope item is a high-level
  overview readable on its own; it never cites a requirement id, of this SRD or
  another, nor rests on another SRD's content ("changes covered by XYZ-12").
  Name the change itself; a related initiative's link goes in a section the
  standard allows for related material. A violation is a finding.
- The in-scope list MAY be deferred: its items derive from the requirements, so
  an SRD MAY leave it holding a single `--- TODO ---` marker line while the
  requirements are still in flux. While the marker stands, the in-scope
  coverage checks (the standard's coverage rule and approval check) are
  suspended — the list is knowingly pending, not defective. Replace the marker
  with real items, in the form the standard sets, derived from the settled
  requirements (see the derivation procedure in `srd-procedures.md`) before
  the SRD reaches the standard's approval status. An unresolved marker is a
  house blocker for approval: always flag it, never keep it silently, and
  never remove it without deriving the items.
- `## TODO` scaffold: an SRD MAY carry a `## TODO` section as its last section
  (where the standard lets extra sections go) — a numbered list of open
  authoring issues the human must return to. These are working notes, not
  requirements: they carry no normative keywords and are exempt from the
  standard's no-example or no-note rule (they sit outside any requirement). It
  MUST be empty or removed before the SRD reaches the standard's approval
  status; a non-empty `## TODO` is a house blocker for approval and is always
  flagged.
- Errata class: a defect whose fix changes only surface form, never what a
  requirement *says*. Classified against the gate, allowlist, and exclusions in
  `errata.md`; `review` groups errata for bulk fixing, `edit autofix` applies
  them.

## Consistency pass

After every significant addition or change, re-read the whole draft from the top
and confirm:

- No earlier requirement was invalidated or contradicted by a later one.
- Every in-scope item is still covered by ≥ 1 requirement; no requirement
  contradicts the out-of-scope list. While the in-scope list holds only the
  `--- TODO ---` marker, skip the coverage check — confirm instead that the
  marker still stands alone (the list is knowingly pending).
- Numbering is still unique and in order, with no collisions or gaps the
  standard forbids.
- Every requirement group is fenced by `---` dividers (the house addition
  above).
- Each term is used consistently (the terminology-consistency house addition
  above; a drift finding cites that, not the pass) and is still defined —
  locally or in the shared glossary. Check every local terms heading against
  each requirement that names its concept: a variant wording (`swap request`
  for `Slot Swap`) is drift.
- Draft scaffolds: any `## TODO` section is the last section and well-formed (a
  numbered list); a non-empty `## TODO` or an unresolved in-scope
  `--- TODO ---` marker is flagged as blocking approval.

This pass is the self-check's feedback loop — repeat it until it is clean.

## Defect classes (Bad → Good)

Requirements below are shown as `[ABC-n] <text>` to keep them apart from any
real format; an SRD writes each identifier in the format the standard sets.

### Terms pollution — behavior hidden in a definition

Bad:
> **Slot Hold** — The time a launch slot stays reserved for a customer after
> they pick it in the Slot Picker. The system MUST release the slot when the
> hold ends without a booking.

Good — definition only; the behavior moves to a requirement:
> **Slot Hold** — The time a launch slot stays reserved for a customer after
> they pick it in the Slot Picker.

### Glossary link repeated on every use

Bad:

```markdown
The Part Kit carries the parts. Each
[Part Kit](../../docs/glossary/terms.md#part-kit) is picked
independently, and a [Part Kit](../../docs/glossary/terms.md#part-kit)
with no parts is skipped.
```

Good — linked on first use, bare after that:

```markdown
The [Part Kit](../../docs/glossary/terms.md#part-kit) carries the
parts. Each Part Kit is picked independently, and a Part Kit with no parts
is skipped.
```

The link is owed once per document, not once per section — a term linked again
three pages later reads like a reference card, whatever strength the standard
gives its first-use link rule. That one link points at the term's own entry,
never at the glossary document as a whole.

### Non-atomic requirement — several rules in one

Bad:
> [ABC-5] The kit label MUST be 100×150 mm, the picker MUST be told to scan
> it, and the kit MUST be marked picked only after the bay confirms receipt.

Good — one rule each (sub-numbered because they form one cluster):
> [ABC-5a] The Part Kit label MUST be printed at 100×150 millimeters.
> [ABC-5b] The instruction text MUST tell the picker to scan the label at the
> door of the assembly bay.
> [ABC-5c] The Part Kit MUST be marked picked only after the assembly bay
> confirms receipt.

### Vague / unverifiable quality

Bad:
> [ABC-7] The system SHALL warn the bay scheduler of a part shortage in good
> time.

Good — concrete, testable:
> [ABC-7] The system MUST warn the bay scheduler of a missing part at least
> 5 working days before stage integration.

### Scope gap — in-scope item with no requirement

Bad: the in-scope list declares "kit labels" but no requirement addresses
it.
Good: either add a requirement that covers kit labels, or narrow the scope
item to what the requirements actually deliver.

### Duplicate / overlapping requirements (consistency)

Two numbered requirements stating the same rule in different words. Keep the
clearer one; remove or merge the other so a reviewer never has to reconcile them.

### Terminology inconsistency (house: terminology consistency)

Using `hot-fire`, `static fire`, and `test firing` interchangeably when the
feature is specifically one of them. Choose one term, define it, and use it
everywhere.

## Good atomic requirements

Each states one rule, names `the system` (or a defined subject), uses an
all-capitals normative keyword, and is verifiable:

> [ABC-2a] A Customer Mission's Swap Deadline MUST default to 14 days before
> its booked Launch Slot.
> [ABC-2b] The Swap Deadline MUST NOT be later than 7 days before the booked
> Launch Slot.
> [ABC-4b] When a slot swap arrives after the Swap Deadline has passed, the
> system MUST reject the swap and MUST NOT release the booked Launch Slot.
