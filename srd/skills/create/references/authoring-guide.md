# SRD Authoring Guide — House Extensions and Defect Classes

Practical guidance that extends the SRD standard in
[srd-standard.md](srd-standard.md). The standard's rules are normative; the
items here are this project's additions plus worked examples that help the agent
draft well and recognize defects during the self-check.

**These examples never go into an SRD.** Every `Bad`/`Good` pair below is
authoring guidance only. A real SRD carries the rule and nothing more (REQ-7).

## Contents

- House additions to the rules
- Errata class
- Consistency pass
- Defect classes (Bad → Good)
- Good atomic requirements

## House additions to the rules

- **US English.** Write SRDs in US English: `color`, `behavior`, `standardize`,
  `analyze`, `center` — not `colour`, `behaviour`, `standardise`. The self-check
  flags British spellings. (This governs the SRD artifact only.)
- **Sub-numbering allowed.** Within a group, tightly-coupled requirements MAY use
  letter suffixes — `**GR-1a:**`, `**GR-1b:**` — when it aids readability. Keep
  it shallow; do not nest deeper than one letter. Plain `**GR-1:**`, `**GR-2:**`
  remains the default; reach for suffixes only when several rules form one tight
  cluster.
- **STR-9 "will and will not do".** An introduction satisfies STR-9 with its
  purpose plus a high-level account of what the system *will* do; the exclusions
  ("will not") are carried by Out of Scope, not restated in the intro. Do not
  raise an intro finding for a missing explicit "will not do" when Out of Scope
  is present.
- **Terminology consistency.** Use one term per concept throughout. Do not mix
  synonyms for the same thing (e.g. `MFA` / `2FA` / `two-factor`); pick one and
  define it once.
- **Template wiki macros are deliberate.** The template's `[[TOC]]`, the
  `[[!Status]]` macro, and the `[!INFO]` notice target the wiki the SRD is
  exported to, not GFM — do not "fix" them to GitHub forms.
- **In Scope MAY be deferred.** In Scope items derive from the requirements
  (SCO-2), so an SRD MAY leave `### In Scope` holding a single `--- TODO ---`
  marker line while the requirements are still in flux. While the marker stands,
  the In-Scope-coverage checks (SCO-2, Quality Bar 2) are suspended — In Scope
  is knowingly pending, not defective. Replace the marker with real `SC-n` items
  derived from the settled requirements (see the derivation procedure in
  [srd-procedures.md](srd-procedures.md)) before the SRD is `ACCEPTED`. An
  unresolved marker is a house blocker for acceptance: always flag it, never
  keep it silently, and never remove it without deriving the items.
- **`## TODO` scaffold.** An SRD MAY carry a `## TODO` section as its last
  section (after Requirements; STR-14) — a numbered list of open authoring
  issues the human must return to. These are working notes, not requirements:
  they carry no normative keywords and are exempt from REQ-7 (they sit outside
  any requirement). It MUST be empty or removed before the SRD is `ACCEPTED`; a
  non-empty `## TODO` is a house blocker for acceptance and is always flagged.
- **Errata class (mechanical, meaning-preserving).** A defect whose fix changes
  only surface form, never what a requirement *says*, is **errata** — safe to
  apply in bulk without per-item review. `review` groups errata for bulk fixing;
  `edit autofix` applies them. The gate, the allowlist, and the exclusions are
  in [Errata class](#errata-class) below; classify against them, not by feel.

## Errata class

Errata is the bulk-appliable class: `review` collects it under `## Errata` and
`edit autofix` applies the whole block behind one confirmation. Because nobody
reviews the fixes individually, the class is drawn to make a false positive
impossible rather than unlikely.

### The gate

A finding is errata **only if** its fix can be stated as an exact literal
substitution — `old → new` — anchored to one named id or verbatim heading,
where `old` appears in that anchor and nowhere ambiguous within it. If the fix
has to be described in prose ("reword", "restate with the system as subject",
"make it consistent"), it is **not** errata, however small it looks.

Three consequences:

- `old` and `new` must survive the review file's 80-column wrapping — keep
  each under roughly 40 characters, and never let a substitution straddle a
  line break. A fix that cannot be quoted that tightly is not errata.
- **Whitespace and glyph fixes carry a class plus a neighboring word, never a
  literal span** — quoting whitespace is forbidden (wrapping destroys the
  proof), so state "two consecutive spaces before the word *in*" and let
  `edit autofix` derive the canonical fix from the class.
- One fix repeated identically across sites is one finding, but it MUST name
  every site, so `autofix` can verify it found exactly that many.

### Errata classes (allowlist)

Nothing outside this list is errata.

- **Misspelling of a clearly-intended word** —
  `Authentiction → Authentication`, `massage → message`, `U ser → User`.
  The intended word must be beyond doubt from the sentence.
- **British → US spelling** — `behaviour → behavior`, `grey → gray`,
  `standardised → standardized`, `cancelled → canceled`.
- **Whitespace** — trailing spaces; two consecutive spaces where one belongs;
  a space trapped inside a bold identifier.
- **Glyph** — a curly quote closing with the wrong direction; a hyphen where a
  parenthetical dash belongs; a stray backslash or other leftover markup glyph.
- **Emphasis markers** — unbalanced or stray `**`; bold leaking into the
  middle of a sentence; a bolded section heading; a malformed bold identifier
  (`**AC-3: ** → **AC-3:** `).
- **Missing terminal period** on a requirement.
- **Closed-form orthography** — `can not → cannot`, and like joins or splits
  where the part of speech leaves one correct form.
- **A uniquely-determined function word** — an article, preposition, or
  infinitive `to` whose absence is ungrammatical and whose insertion is the only
  grammatical repair: `force users re-authenticate → force users to
  re-authenticate`. If more than one insertion works, it is not errata.
- **Heading case matched to the document's own convention** —
  `## In scope → ## In Scope` when every sibling heading is title-cased.
- **Boilerplate the standard fixes verbatim** — the STR-8 keyword notice.

### Never errata (exclusions)

These stay out of `## Errata` even when a literal substitution exists:

- Text inside a code span, a URL, a quoted UI string, or a product, device, or
  proper name — the "misspelling" may be the real spelling.
- Inserting or deleting a **content** word (noun, verb, adjective) or any
  normative keyword.
- Any change to a requirement identifier — its spelling, number, prefix, or
  order.
- Subject, voice, or mood: passive → active, or "the user interface MUST" →
  "the system MUST" (LANG-1). These are rewrites, not surface form.
- Capitalizing a term to its glossary form. The question is whether the site
  means the defined term or the generic sense — author judgment, not surface
  form.
- Line wrapping or reflow.
- Any case with two plausible corrections, or where the intended word is
  genuinely in doubt. Classify **conservatively**: when in doubt, not errata.

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
     its localId is annotated at the section. untranscribed example blocks —
     source examples with no section here yet; check them on the next
     page_version bump:
     2b66f741-45ad-4225-8f24-c69401b968d5 (follows LANG-1),
     c6f67fef-67b2-441f-9341-66c10dcd685e (follows LANG-3),
     6fec97d9-b0a9-4d67-a462-2f51e0c35bd8 (follows LANG-6),
     ee6f5ac1-261a-42bc-8ad7-70c0c2934499 (follows LANG-7),
     d724bbc4-efcd-49a8-abd7-f0bd6200cd0f (follows REQ-2) -->

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
