# review

Reviews an existing **Software Requirement Document (SRD)** — one written by
someone else — for consistency, logic, and conformance to the **SRD standard**.
It reads the whole document, checks it
against the standard, and writes the findings to a review file beside the
source.

It is a **read-only review** skill: it never edits the SRD. It produces findings
the author acts on. To create a new SRD, use `create`.

## When to Use

- Someone hands you an SRD and asks whether it meets the house standard.
- Before a requirements review meeting or sign-off.
- After an author has fixed a prior round, to confirm the fixes landed and
  nothing new broke.
- When you want a shareable issue list for an email or ticket.

## How It Works

The rules and checklist are reused from `create` —
`../create/references/srd-standard.md` (STR/STA/LANG/REQ/GLO/SCO/MD/Quality
Bar), `../create/references/srd-checklist.md` (the action-neutral
verification checklist the review runs), and
`../create/references/authoring-guide.md` (house extensions + defect
classes). review adds only the review method; it never restates a rule. Do
not move or rename `create`, or this skill loses its standard.

The review file is always `<srd>.review.md` next to the source. Findings are
grouped **by document section** (Metadata → Introduction → Glossary → Scope →
Requirements), each citing a rule id and tagged:

- **blocker** — breaks Quality-Bar acceptance (non-atomic, unverifiable, scope
  gap, undefined term, rule hidden in glossary/metadata, duplicate/out-of-order
  id, missing required link or back-link, invalid Status).
- **major** — real but non-blocking (style, terminology drift, overlap).
- **minor** — cosmetic (wrap, spelling, spacing).

Unlike `create`, the review applies the **full** standard — including the
owners count, Initiative/Designs links and back-links (STR-2..7) and Status
rules (STA-*) that authoring leaves as placeholders.

## Usage

```
/review path/to/srd.md            review (default): write srd.review.md
/review path/to/srd.md walk       interactive, section by section
/review path/to/srd.md check      re-check srd.review.md vs the current SRD
/review path/to/srd.md feedback   terse plain-text list for email/ticket
```

## What to Expect

- A `srd.review.md` file with all findings grouped by section, each tagged and
  citing its rule id, plus a one-line severity tally.
- On a re-run, resolved findings struck through and new ones appended — the file
  accumulates rather than being rewritten.
- The skill never edits the SRD and never declares it `Accepted` — acceptance is
  a human decision.

## Evaluations

### 1. Default review of a flawed SRD

**Request:** `/review specs/login.md` where `GR-3a` reads "The system SHALL
validate the token and log the attempt", an `In Scope` item has no requirement,
and a line runs to 96 columns.

**Expected behavior:**
- Reads the whole SRD, then writes `specs/login.review.md` — makes no edit to
  `login.md`.
- Groups findings by document section; tags the two-rule requirement
  **blocker** citing REQ-1, the uncovered scope item **blocker** citing SCO-2,
  and the long line **minor** citing MD-2.
- Closes with a per-severity count and whether a blocker stands between the SRD
  and the Quality Bar.

### 2. Applies rules create only stubs

**Request:** `/review specs/api.md` on an SRD whose metadata lists a single
owner, has no Initiative link, and is marked `Status: Accepted` with no approved
design though it changes the UI.

**Expected behavior:**
- Flags the single owner (STR-2), the missing Initiative link and back-link
  (STR-3/4), and the `Accepted` status without an approved design (STA-2) — all
  **blocker** — instead of treating them as expected placeholders.
- Records them under the Metadata section of the review file.

### 3. Check a prior review after fixes

**Request:** `/review specs/login.md check` with an existing
`specs/login.review.md`.

**Expected behavior:**
- Classifies each prior finding fixed / partial / not-addressed against the
  current text, in a short status table.
- Flags any new defect introduced by the edits.
- Updates `login.review.md`: strikes resolved findings, annotates partials with
  `*(Partial — …)*`, appends new defects, and bumps the `Updated:` date.

### 4. Feedback export for a ticket

**Request:** `/review specs/login.md feedback`.

**Expected behavior:**
- Emits plain text grouped by section heading, one bullet per open issue, no
  file write.
- Keeps the SRD's own requirement ids (e.g. `GR-3a:`) but drops the standard
  rule-id citations and severity tags; uses no markdown beyond bullets.
- Omits any issue already resolved.

### 5. Walk records only confirmed findings

**Request:** `/review specs/login.md walk`.

**Expected behavior:**
- Goes section by section, presenting each section's findings and waiting for
  the user to confirm which to keep before recording anything.
- Writes only confirmed findings to `login.review.md`, as author-facing
  guidance, and never edits `login.md`.

### 6. Terse output

**Request:** `/review specs/login.md`.

**Expected behavior:**
- No preamble or narration ("I'll read the SRD now…"); opens with the result.
- Writes the findings to the review file and closes with a short pointer plus
  per-severity counts — no re-listing of the findings already written to the
  file.
