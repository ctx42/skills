---
name: review
description: >
  Reviews an existing Software Requirement Document (SRD) written by someone
  else for consistency, logic, and conformance to the SRD standard, and
  writes the findings to a review file beside the source. Use when asked to
  review, audit, critique, or check an SRD or software requirements document, or
  to re-check whether prior review findings were fixed. Read-only: it never
  edits the source; it produces findings grouped by document section, each
  citing a standard rule id and tagged blocker, major, or minor.
license: MIT
---

# review

Review an SRD someone else wrote and report what fails the SRD standard. This
skill is **read-only** — it never edits the source. It produces findings the
author acts on.

## Self-learning

Read this skill's lessons first and obey them: the sibling `LESSONS.md`, plus —
when this skill's directory is not writable (an installed copy) —
`$HOME/.agent-data/ctx42-skills/lessons/srd/review.md`. When the user corrects
you, or you catch your own mistake, append the fix as a one-line rule to
whichever is writable (the sibling in a source checkout, else the `.agent-data`
file, creating it), then report where — so it never recurs.

## Boundaries

- **Role:** the read-only reviewer of an SRD written by someone else. Produce
  findings; the author acts on them.
- **Owns:** the creation and structure of the `<srd>.review.md` file beside the
  source, plus the `walk`, `feedback`, and `check` modes. `edit` may delete findings
  it has fully fixed; no other skill writes the file.
- **Must not:** edit the source SRD or fix anything; restate or invent rules —
  defer all format, style, logic, and rules to `create`'s reference files.

## Sources of truth

The rules, checklist, and defect classes live with `create`; this skill
reuses them and never restates a rule. **This skill depends on
`../create/references/*` — do not move or rename `create`. If any
referenced file is missing at run time, stop and tell the user; do not
proceed.** Read these before reviewing:

- [../create/references/srd-standard.md](../create/references/srd-standard.md)
  — the rules (`STR`, `STA`, `LANG`, `REQ`, `GLO`, `SCO`, `MD`, Quality
  Bar). Every finding cites one of these ids.
- [../create/references/srd-checklist.md](../create/references/srd-checklist.md)
  — the action-neutral verification checklist the review runs.
- [../create/references/authoring-guide.md](../create/references/authoring-guide.md)
  — house extensions (US English, sub-numbering, terminology consistency) and
  the Bad→Good defect classes to recognize; includes the consistency pass.

**Apply the full rule set.** `create` leaves STR-2..7 (≥ 2 owners,
Initiative link + back-link, Designs link + back-link, Designs `N/A` when no UI
change) and STA-* (valid Status; not `Accepted` without an approved design or the
Quality Bar) as placeholders. A finished SRD under review must satisfy them —
flag every gap.

## Severity

Tag each finding:

- **blocker** — breaks Quality-Bar acceptance: non-atomic (REQ-1), unverifiable
  (REQ-5/6), uncovered `In Scope` item (SCO-2), requirement contradicting `Out
  of Scope` (SCO-3), undefined term (GLO-3/STR-10), rule hidden in a glossary
  entry or metadata (GLO-1/2), duplicate or out-of-order id (REQ-3/4), missing
  required link or back-link (STR-2..7), invalid or over-claimed Status (STA-*).
- **major** — real defect, does not block: style (LANG-1/2/5/6/7), terminology
  drift, overlapping or duplicate requirements.
- **minor** — cosmetic: line over 80 columns (MD-2), British spelling, spacing,
  punctuation.

## Modes

The review file is always `<srd>.review.md` next to the source — auto-derived,
never passed as an argument. Detect the mode from the user's words:

- `/review path/to/srd.md` → **review** (default): read the whole SRD, write
  the review file.
- `/review path/to/srd.md walk` → **walk**: interactive, section by section;
  record only findings the user confirms.
- `/review path/to/srd.md check` → **check**: re-check the existing review
  file against the current SRD; mark each finding fixed / partial / not, flag
  new defects, update the file.
- `/review path/to/srd.md feedback` → **feedback**: emit a terse plain-text
  issue list for an email or ticket. No file write.

In every mode, report tersely: no preamble or narration; state each fact once;
don't restate output the user can already see.

## Review file format

Group findings **by document section** in this order: Metadata, Introduction,
Glossary, Scope, Requirements. Omit a section with no findings. One bullet per
finding: severity, the offending location or id, the problem, the fix, and the
rule id. Indent continuation lines two spaces.

```
# SRD Review — <Document Title>

Prepared: YYYY-MM-DD
Updated: YYYY-MM-DD
Source: `path/to/srd.md`

## Requirements

- [blocker] GR-3a: states two rules ("validate ... and log ...") — split into
  one rule each. (REQ-1)
- [major] GR-7 and GR-9 state the same limit in different words — merge or
  remove one. (consistency)
- [minor] line 88 exceeds 80 columns — wrap. (MD-2)
```

## review (default)

1. Read the entire SRD top to bottom.
2. Run every check in
   [../create/references/srd-checklist.md](../create/references/srd-checklist.md)
   against it, including the consistency pass.
3. Write all findings to the review file, grouped and tagged as above.
4. If the review file already exists, do not rewrite it — delete resolved
   items, keep open ones, append new findings to their section, and bump
   `Updated:`.
5. Close with one line: counts per severity, and whether any blocker stands
   between the SRD and the Quality Bar.

## walk

Go section by section in document order. For each section:

1. Read it and identify every issue.
2. Present the findings — problem and fix for each. Record nothing yet.
3. Wait for the user to confirm which to keep (all, some, none).
4. Append only confirmed findings to the review file, written as author-facing
   guidance. Create the file before the first write; bump `Updated:` on each.
5. Move on only after the user confirms or skips. Never edit the source.

## check

Given the current SRD and its existing review file:

1. For each finding, judge it **fixed**, **partial**, or **not addressed**
   against the current text.
2. Run the consistency pass again and flag any new defect the edits introduced.
3. Update the review file: delete resolved findings, append `*(Partial — …)*`
   to partials, add new defects to their section, re-tally any counts, and bump
   `Updated:`. When the last finding is gone, delete the whole file.
4. Report a short status table: finding, current state, assessment.

## feedback

Emit plain text for an email or ticket — no file write:

- Title: `<Document Title> — Review Feedback`.
- Group by section name as a plain heading (no markdown symbols).
- One bullet per open issue. Keep the SRD's own requirement id (e.g.
  `GR-3a:`), then a one-line problem-and-fix. Drop standard rule-id citations
  and severity tags. No bold, no multi-line bullets.
- Omit resolved issues.

## Consistency pass

Run the consistency pass in
[../create/references/authoring-guide.md](../create/references/authoring-guide.md)
(also summarized in the Consistency section of the checklist). Report each
consistency finding under the section where the conflict surfaces, citing the
rule id or `(consistency)`.
