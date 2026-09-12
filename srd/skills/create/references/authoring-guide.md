# SRD Authoring Guide — House Extensions and Defect Classes

Practical guidance that extends the SRD standard in
[srd-standard.md](srd-standard.md). The standard's rules are normative; the
items here are this project's additions plus worked examples that help the agent
draft well and recognize defects during the self-check.

**These examples never go into an SRD.** Every `Bad`/`Good` pair below is
authoring guidance only. A real SRD carries the rule and nothing more (REQ-7).

## Contents

- House additions to the rules
- Consistency pass
- Defect classes (Bad → Good)
- Good atomic requirements

## House additions to the rules

- Write SRDs in US English: `color`, `behavior`, `standardize`,
  `analyze`, `center` — not `colour`, `behaviour`, `standardise`. The self-check
  flags British spellings. (This governs the SRD artifact only.)
- Sub-numbering is allowed: within a group, tightly-coupled requirements MAY use
  letter suffixes — `**GR-1a:**`, `**GR-1b:**` — when it aids readability. Keep
  it shallow; do not nest deeper than one letter. Plain `**GR-1:**`, `**GR-2:**`
  remains the default; reach for suffixes only when several rules form one tight
  cluster.
- STR-9 "will and will not do": an introduction satisfies STR-9 with its
  purpose plus a high-level account of what the system *will* do; the exclusions
  ("will not") are carried by Out of Scope, not restated in the intro. Do not
  raise an intro finding for a missing explicit "will not do" when Out of Scope
  is present.
- Terminology consistency: use one term per concept throughout. Do not mix
  synonyms for the same thing (e.g. `MFA` / `2FA` / `two-factor`); pick one and
  define it once. Qualify overloaded terms ("tag", "metadata", "header",
  "channel") with what they belong to ("a sound file's `sen.kind` metadata
  tag"); terseness never excuses a term that resolves differently in another
  document.
- Glossary is conditional (STR-10 "terms that need a definition"): never
  require a Glossary section when nothing needs defining. Proper names
  (product or module names, external tools, device models) are not concepts
  and are not GLO-3 gaps.
- Plain headings: never bold a heading (`### **X**`); de-bold existing ones.
- Link, do not restate: when a requirement would repeat rules an authoritative
  platform document defines, link that document and state only the SRD-level
  constraint.
- Plain language: short sentences, everyday verbs, at most one condition
  clause; never stack nested qualifiers. The linked platform document carries
  the precision.
- A device or product model named in a requirement is the correct scope when
  the UI surface or feature exists only for those models; never propose
  generalizing it away.
- No catch-all requirement ("features not addressed behave identically"): an
  SRD specifies only what changes; unspecified areas are unchanged by default,
  and such a rule is weakly verifiable (REQ-5, LANG-7).
- Narrowing is layering, not contradiction: an SRD that offers less than a
  platform document says the system can do is not a corpus gap and the
  platform document is not wrong. A role or setting that restores the full
  capability is the tell that both statements hold.
- `REQ` is a legitimate requirement prefix: the standard's own `STR-*`/`REQ-*`
  ids must not be pasted into an SRD, but the letter codes are not reserved.
  Never raise a prefix "collision" with the standard as a finding.
- Template wiki macros are deliberate: the template's `[[TOC]]`, the
  `[[!Status]]` macro, and the `[!INFO]` notice target the wiki the SRD is
  exported to, not GFM — do not "fix" them to GitHub forms.
- In Scope MAY be deferred: In Scope items derive from the requirements
  (SCO-2), so an SRD MAY leave `### In Scope` holding a single `--- TODO ---`
  marker line while the requirements are still in flux. While the marker stands,
  the In-Scope-coverage checks (SCO-2, Quality Bar 2) are suspended — In Scope
  is knowingly pending, not defective. Replace the marker with real `SC-n` items
  derived from the settled requirements (see the derivation procedure in
  [srd-procedures.md](srd-procedures.md)) before the SRD is `ACCEPTED`. An
  unresolved marker is a house blocker for acceptance: always flag it, never
  keep it silently, and never remove it without deriving the items.
- `## TODO` scaffold: an SRD MAY carry a `## TODO` section as its last
  section (after Requirements; STR-14) — a numbered list of open authoring
  issues the human must return to. These are working notes, not requirements:
  they carry no normative keywords and are exempt from REQ-7 (they sit outside
  any requirement). It MUST be empty or removed before the SRD is `ACCEPTED`; a
  non-empty `## TODO` is a house blocker for acceptance and is always flagged.
- Errata class: a defect whose fix changes only surface form, never what a
  requirement *says*. Classified against the gate, allowlist, and exclusions in
  [errata.md](errata.md); `review` groups errata for bulk fixing, `edit autofix`
  applies them.

## Consistency pass

After every significant addition or change, re-read the whole draft from the top
and confirm:

- No earlier requirement was invalidated or contradicted by a later one.
- Every `In Scope` item is still covered by ≥ 1 requirement (SCO-2); no
  requirement contradicts `Out of Scope` (SCO-3). While `### In Scope` holds
  only the `--- TODO ---` marker, skip the coverage check — confirm instead that
  the marker still stands alone (In Scope is knowingly pending).
- Numbering is still unique and in order, with no collisions or large gaps.
- Each term is used consistently and is still defined (locally or in the company
  glossary).
- Draft scaffolds: any `## TODO` section is the last section and well-formed (a
  numbered list); a non-empty `## TODO` or an unresolved In Scope `--- TODO ---`
  marker is flagged as blocking acceptance.

This pass is the self-check's feedback loop — repeat it until it is clean.

## Defect classes (Bad → Good)

<!-- Each Bad→Good section below transcribes an upstream source example block;
     its localId is annotated at the section. Untranscribed ids are listed in
     dev/srd-untranscribed-examples.md. -->

### Glossary pollution — behavior hidden in a definition (GLO-1/2)
<!-- expand: 563d87a5-e660-4203-887b-17c549fbd7f2 (follows GLO-1) -->

Bad:
> **Recovery Codes** — One-time codes that let a user regain access when their
> primary method is unavailable. The system MUST generate ten codes at setup and
> invalidate each after first use.

Good — definition only; the behavior moves to a requirement:
> **Recovery Codes** — One-time codes that let a user regain access when their
> primary authentication method is unavailable.

### Non-atomic requirement — several rules in one (REQ-1)
<!-- expand: 9f74c18d-837b-46c7-aaff-b27e00b6936b (follows REQ-1) -->

Bad:
> **GR-5:** The QR code MUST be 300×300 px, the user MUST be told to scan it, and
> setup MUST complete only after the device confirms registration.

Good — one rule each (sub-numbered because they form one cluster):
> **GR-5a:** The setup QR code MUST be rendered at 300×300 pixels.
> **GR-5b:** The instruction text MUST tell the user to scan the code with a
> compatible mobile device.
> **GR-5c:** The setup step MUST be marked complete only after the device
> registers the passkey.

### Vague / unverifiable quality (REQ-6)
<!-- expand: ba9af145-8228-428f-bafa-e1508d24b9ec (follows REQ-6) -->

Bad:
> **GR-7:** The system SHALL use strong authentication appropriate to the data.

Good — concrete, testable:
> **GR-7:** The system MUST require multi-factor authentication for every
> administrative action on data classified `Restricted`.

### Scope gap — In Scope item with no requirement (SCO-2)
<!-- expand: 01267af0-60b6-4c15-a8e6-545c66d420e8 (follows SCO-2) -->

Bad: `In Scope` declares "file handling" but no requirement addresses it.
Good: either add a requirement that covers file handling, or narrow the scope
item to what the requirements actually deliver.

### Duplicate / overlapping requirements (Quality Bar 2, consistency)

Two numbered requirements stating the same rule in different words. Keep the
clearer one; remove or merge the other so a reviewer never has to reconcile them.

### Terminology inconsistency

Using `MFA`, `2FA`, and `two-factor authentication` interchangeably when the
feature is specifically one of them. Choose one term, define it, and use it
everywhere.

## Good atomic requirements

Each states one rule, names `the system` (or a defined subject), uses an
all-capitals normative keyword, and is verifiable:

> **GR-2a:** A user account's Session Timeout MUST default to the Default Session
> Timeout of the Security Policy assigned to that account.
> **GR-2b:** The Session Timeout MUST NOT be longer than the Security Policy's
> Maximum Session Timeout.
> **GR-4b:** When a request arrives after the Session Timeout has elapsed, the
> system MUST reject the request and MUST NOT reveal whether the session ever
> existed.
