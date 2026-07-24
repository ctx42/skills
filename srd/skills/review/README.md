# review

Reviews an existing **Software Requirement Document (SRD)** — one written by
someone else — for consistency, logic, and conformance to the **SRD standard**.
It reads the whole document, checks it
against the standard, and writes the findings to a review file beside the
source.

It is a **read-only review** skill: it never edits the SRD. It produces findings
the author acts on. To create a new SRD, use `create`.

## Usage

```
/review path/to/srd.md            review (default): resolve fixed + append new
/review path/to/srd.md walk       interactive, section by section
/review path/to/srd.md check      re-verify open findings vs the current SRD
/review path/to/srd.md check #4,6  re-verify only findings #4 and #6
/review path/to/srd.md errata     re-sort existing findings into ## Errata
/review path/to/srd.md feedback   terse plain-text list of open tasks
```

## When to Use

- Someone hands you an SRD and asks whether it meets the house standard.
- Before a requirements review meeting or sign-off.
- After an author has fixed a prior round, to confirm the fixes landed and
  nothing new broke.
- When you want a shareable issue list for an email or ticket.

## How It Works

The rules are reused from `create` —
`../create/references/srd-standard.md` (STR/STA/LANG/REQ/GLO/SCO/Quality
Bar; the review checks every rule) and
`../create/references/authoring-guide.md` (house extensions + defect
classes). review adds only the review method; it never restates a rule. Do
not move or rename `create`, or this skill loses its standard.

The review file is always `<srd>.review.md` next to the source. Each finding
carries a **permanent global number** (`#1..#N`, never reused or renumbered) and
is **atomic** — one indivisible fix, verifiable by a single yes/no. Open
findings are `[ ]` checkboxes grouped **by document section** (Metadata →
Introduction → Glossary → Scope → Requirements), each citing a rule id
(namespaced `SRD:`, e.g. `(SRD:REQ-1)`) and tagged. Mechanical,
meaning-preserving findings (spelling, punctuation, stray emphasis, spacing)
are collected instead into a `## Errata` block at the very top, so the author
can bulk-apply them with `edit <srd> autofix`. File metadata (`prepared`,
`updated` with a timestamp, `source`) sits in YAML frontmatter. Below the open
findings, a `## Resolved` section holds ticked `[x]` findings (flat,
sorted by number) and a `## Withdrawn` section holds findings dropped as
invalid. Findings are separated by a blank line so a long list reads as
distinct blocks. Tags:

- **blocker** — breaks Quality-Bar acceptance (non-atomic, unverifiable, scope
  gap, undefined term, rule hidden in glossary/metadata, duplicate/out-of-order
  id, missing required link or back-link, invalid Status).
- **major** — real but non-blocking (style, terminology drift, overlap).
- **minor** — cosmetic (wrap, spelling, spacing).

Unlike `create`, the review applies the **full** standard — including the
owners count, Initiative/Designs links and back-links (STR-2..7) and Status
rules (STA-*) that authoring leaves as placeholders.

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
  **blocker** citing REQ-1 and the uncovered scope item **blocker** citing
  SCO-2. Collects the British spelling into the `## Errata` block at the top,
  tagged **minor** citing LANG-1.
- Closes with a per-severity count and whether a blocker stands between the SRD
  and the Quality Bar.

### 2. Applies rules create only stubs

**Request:** `/review specs/api.md` on an SRD whose metadata lists a single
owner, has no Initiative link, and is marked `Status: ACCEPTED` with no approved
design though it changes the UI.

**Expected behavior:**
- Flags the single owner (STR-2), the missing Initiative link and back-link
  (STR-3/4), and the `ACCEPTED` status without an approved design (STA-2) — all
  **blocker** — instead of treating them as expected placeholders.
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
  but drops the checkbox, the standard rule-id citations, and severity tags;
  uses no markdown beyond bullets.
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
  (LANG-3); British spellings (minor).
- Serves as the before/after gate whenever the shared references change: the
  finding set must not shrink.

### 7. Terse output

**Request:** `/review specs/login.md`.

**Expected behavior:**
- No preamble or narration ("I'll read the SRD now…"); opens with the result.
- Writes the findings to the review file and closes with a short pointer plus
  per-severity counts — no re-listing of the findings already written to the
  file.

### 8. Errata retrofit of an existing review

**Request:** `/review specs/login.md errata` with an existing
`specs/login.review.md` written before the `## Errata` block existed, holding a
British-spelling finding `#4` under Requirements and a scope blocker `#2`.

**Expected behavior:**
- Moves `#4` into a `## Errata` block at the top, keeping its number, `[minor]`
  tag, and citation; leaves the blocker `#2` under its section.
- Reclassifies only — hunts no new defects; a second run changes nothing
  (idempotent); bumps the `updated:` timestamp and reports the moved number.
