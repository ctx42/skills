# review

Reviews an existing Software Requirement Document (SRD) for consistency, logic,
and conformance to the SRD standard, writing findings to a review file beside
the source — read-only; it never edits the SRD.

## Usage

```
/review path/to/srd.md             review (default): resolve fixed + append new
/review path/to/srd.md walk        interactive, section by section
/review path/to/srd.md check       re-verify open findings vs the current SRD
/review path/to/srd.md check #4,6  re-verify only findings #4 and #6
/review path/to/srd.md errata      re-sort existing findings into ## Errata
/review path/to/srd.md feedback    terse plain-text list of open tasks
```

## When to Use

- Someone hands you an SRD and asks whether it meets the house standard.
- Before a requirements review meeting or sign-off.
- After an author has fixed a prior round, to confirm the fixes landed and
  nothing new broke.
- When you want a shareable issue list for an email or ticket.

To create a new SRD, use `create`; to apply findings, use `edit`.

## How It Works

The rules are reused from `create`: `../create/references/srd-standard.md`
(STR/STA/LANG/REQ/GLO/SCO/Quality Bar; the review checks every rule),
`../create/references/authoring-guide.md` (house additions, consistency pass,
defect classes), `../create/references/errata.md` (the bulk-fix errata class),
and `../create/references/doc-corpus.md` (how to reach the documentation
corpus). review adds only the review method; it never restates a rule. Do not
move or rename `create`, or this skill loses its standard.

When a documentation corpus is reachable, the review also checks every claim
about existing system behavior against it. A claim the corpus contradicts is a
`reference` finding; one it cannot confirm is a doc gap handed to
`srd:report-doc-gap`, never a review finding. Pending doc gaps from a prior
session are drained when a review starts; the gaps a run buffers are offered
for filing when it finishes.

The review file is always `<srd>.review.md` beside the source. Each finding
carries a permanent global number (`#1..#N`, never reused or renumbered) and is
atomic — one indivisible fix, verifiable by a single yes/no. Open findings are
`[ ]` checkboxes grouped by document section (Metadata → Introduction →
Glossary → Scope → Requirements), each citing a rule id (namespaced `SRD:`,
e.g. `(SRD:REQ-1)`; `(SRD:house)` for house additions such as US English) and
tagged. Mechanical, meaning-preserving findings (spelling, grammar repairs with
one correct form, punctuation, stray emphasis, spacing) are collected instead
into a `## Errata` block at the very top, so the author can bulk-apply them
with `edit <srd> autofix`. An errata finding always states its fix as an exact
substitution — `` `old` → `new` ``, or a whitespace/glyph class plus a
neighboring word — which is what makes it appliable unreviewed; a fix that
needs prose to describe is not errata. File metadata (`prepared`, `updated`
with a timestamp, `source`) sits in YAML frontmatter. Below the open findings,
a `## Resolved` section holds ticked `[x]` findings (flat, sorted by number)
and a `## Withdrawn` section holds findings dropped as invalid. Findings are
separated by a blank line so a long list reads as distinct blocks. Severity
tags:

- `blocker` — breaks Quality-Bar acceptance (non-atomic, unverifiable, scope
  gap, undefined term, rule hidden in glossary/metadata, duplicate/out-of-order
  id, missing required forward link, invalid Status, unresolved draft scaffold).
- `major` — real but non-blocking (style, terminology drift, overlap).
- `minor` — cosmetic (spelling, spacing, punctuation).

Every finding also carries a category naming what kind of defect it is, in the
same bracket as the severity and after it — `[major, logical]`. A finding that
genuinely carries two gets both, primary first: `[major, logical, redundancy]`.
Severity always occupies the first slot, so the two never blur. The table is in
precedence order; when a finding fits more than one, the higher entry leads.

| Category      | What it means                                                 | Typical rules               |
| ------------- | ------------------------------------------------------------- | --------------------------- |
| structure     | Required part of the document absent, or Status invalid       | STR-*, STA-*                |
| logical       | Two rules conflict, or no rule covers a case                  | consistency                 |
| coverage      | In Scope item with no requirement; rule stated only in a Note | SCO-2, SCO-3                |
| reference     | A link, ticket id, or claim about the live system is wrong    | —                           |
| redundancy    | Two rules say the same thing, or one subsumes the other       | consistency                 |
| verifiability | Vague quality, unmeasurable criterion, open-ended list        | REQ-5, REQ-6, LANG-7        |
| atomicity     | More than one rule per item; example or note inside a rule    | REQ-1, REQ-7, LANG-5, SCO-1 |
| terminology   | One concept under many names; undefined term; casing drift    | GLO-1, GLO-2, GLO-3         |
| linguistic    | Grammar, spelling, missing word, wrong subject or keyword     | LANG-1..4, LANG-6           |
| format        | Markup, bold identifiers, id numbering, punctuation, spacing  | REQ-2, REQ-3, REQ-4, REQ-8  |

Category is independent of the `## Errata` block: an errata finding is always
`format` or `linguistic`, but many `format` and `linguistic` findings are not
errata — renumbering ids and rewriting a requirement's subject both change
meaning or references, so they need author judgment.

Unlike `create`, the review applies the full standard — including the owners
count, the forward Initiative/Designs links (STR-2/3/5/7) and the Status rules
(STA-*) that authoring leaves as placeholders. The back-links (STR-4/6) live in
the external ticket and design tool and are never flagged.

It recognizes the two draft scaffolds (In Scope `--- TODO ---` marker and a
`## TODO` section): while the marker stands it does not flag SCO-2 against In
Scope, and it reports an unresolved marker or a non-empty `## TODO` as a blocker
for acceptance.

## What to Expect

- A `srd.review.md` file: numbered `[ ]` open tasks grouped by section, each
  tagged and citing its rule id, with mechanical fixes collected in a `## Errata`
  block at the top, plus `## Resolved` and `## Withdrawn` sections, and a
  task-oriented closing tally.
- On a re-run, fixed findings are ticked and moved to `## Resolved` (keeping
  their number) and new ones appended — the file is updated in place, never
  rewritten from scratch; numbers are never reused.
- The skill never edits the SRD and never declares it `ACCEPTED` — acceptance is
  a human decision.

## Evaluations

### 1. Default review of a flawed SRD

**Request:** `/review specs/login.md` where `GR-3a` reads "The system SHALL
validate the token and log the attempt", an `In Scope` item has no requirement,
and one requirement uses British spelling.

**Expected behavior:**
- Reads the whole SRD, then writes `specs/login.review.md` — makes no edit to
  `login.md`.
- Groups findings by document section; tags the two-rule requirement
  `[blocker, atomicity]` citing REQ-1 and the uncovered scope item
  `[blocker, coverage]` citing SCO-2. Collects the British spelling into the
  `## Errata` block at the top, tagged `[minor, linguistic]` citing
  `(SRD:house)` and stating the substitution (`` `behaviour` → `behavior` ``).
- Closes with a per-severity count and whether a blocker stands between the SRD
  and the Quality Bar.

### 2. Applies rules create only stubs

**Request:** `/review specs/api.md` on an SRD whose metadata lists a single
owner, has no Initiative link, and is marked `Status: ACCEPTED` with no approved
design though it changes the UI.

**Expected behavior:**
- Flags the single owner (STR-2), the missing Initiative link (STR-3), and the
  `ACCEPTED` status without an approved design (STA-2) — all blocker — instead
  of treating them as expected placeholders.
- Raises no back-link finding (STR-4/6 are external).
- Records them under the Metadata section of the review file.

### 3. Check a prior review after fixes

**Request:** `/review specs/login.md check` with an existing
`specs/login.review.md`.

**Expected behavior:**
- Classifies each open finding fixed / partial / not-addressed against the
  current text, in a short status table keyed by finding number.
- Re-verifies only — does not hunt for new defects.
- Updates `login.review.md`: ticks fixed findings and moves them to
  `## Resolved`, annotates partials with `*(Partial — …)*`, moves any invalid
  finding to `## Withdrawn` with a reason, keeps every number, and bumps the
  `updated:` frontmatter timestamp.

### 4. Feedback export for a ticket

**Request:** `/review specs/login.md feedback`.

**Expected behavior:**
- Emits plain text grouped by section heading, one bullet per open issue, no
  file write; lists the `Errata` group first when it holds open findings.
- Keeps the finding number and the SRD's own requirement id (e.g. `#7 GR-3a:`)
  but drops the checkbox, the rule-id citations, and severity tags; uses no
  markdown beyond bullets.
- Lists open findings only — omits Resolved and Withdrawn.

### 5. Walk records only confirmed findings

**Request:** `/review specs/login.md walk`.

**Expected behavior:**
- Goes section by section, presenting each section's findings and waiting for
  the user to confirm which to keep before recording anything.
- Writes only confirmed findings to `login.review.md`, as author-facing
  guidance, and never edits `login.md`.

### 6. Fixture regression

**Request:** `/review` on `assets/flawed-srd.md` (the bundled deliberately
defective sample).

**Expected behavior:**
- Finds at least: GR-1 non-atomic (REQ-1); duplicate id GR-3 (REQ-3); "fast"
  unverifiable (REQ-6); SC-2 uncovered (SCO-2); GR-4 contradicts OSC-1
  (SCO-3); behavior in the Export Job glossary entry (GLO-1/2); a single owner
  (STR-2); missing Initiative link (STR-3); `ACCEPTED` with an unapproved
  design and unmet Quality Bar (STA-2/STA-3); MUST in the Introduction
  (LANG-3); British spellings (minor, under `## Errata`).
- Serves as the before/after gate whenever the shared references change: the
  finding set must not shrink.

### 7. Terse output

**Request:** `/review specs/login.md`.

**Expected behavior:**
- No preamble or narration ("I'll read the SRD now…"); opens with the result.
- Writes the findings to the review file and closes with a short pointer plus
  per-severity counts — no re-listing of the findings already written to the
  file.

### 8. Errata re-sort of an existing review

**Request:** `/review specs/login.md errata` with an existing
`specs/login.review.md` holding a British-spelling finding `#4` under
Requirements and a scope blocker `#2`, and no `## Errata` block.

**Expected behavior:**
- Moves `#4` into a `## Errata` block at the top, keeping its number, `[minor]`
  tag, category, and citation, and rewriting its prose fix into the substitution
  shape; leaves the blocker `#2` under its section.
- Reclassifies only — hunts no new defects; a second run changes nothing
  (idempotent); bumps the `updated:` timestamp and reports the moved number.

### 9. Facts-vs-corpus pass routes doc gaps

**Request:** `/review specs/gateway.md` with the `srd-doc` corpus reachable,
where `GW-2` states "the gateway retries 3×" and no corpus document states a
retry count, while `GW-5` names a timeout the corpus documents as a different
value.

**Expected behavior:**
- Invokes `srd:report-doc-gap` first to drain gaps left from a prior session,
  then `search`es the corpus for each claim about existing behavior.
- Hands the unconfirmable `GW-2` retry count to `srd:report-doc-gap` as a doc
  gap; it appears nowhere in `gateway.review.md`.
- Records the contradicted `GW-5` timeout as a `reference` finding in the
  review file.
- After the closing tally, offers to work the buffered `GW-2` gap now or later;
  never files it silently.
