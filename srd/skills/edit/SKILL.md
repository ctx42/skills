---
name: edit
description: >
  Interactively improves an existing Software Requirement Document (SRD) by
  editing it in place against the SRD standard, one confirmed change at a
  time. Use when asked to edit, improve, fix, revise, or clean up an SRD, or to
  apply the findings from a review `<srd>.review.md` or pasted feedback.
  Walks the SRD entry by entry, proposes one change at a time with before/after,
  guards requirement ids on approved documents, and re-validates after each
  edit. The write counterpart to the read-only review.
license: MIT
---

# edit

Drive an existing SRD toward the SRD standard by editing the source, **one
confirmed change at a time**. This skill **edits the source file** — it is the
write counterpart to the read-only `review`. It never restates a rule; it
reuses the standard and self-checks every edit against it.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/srd/edit.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.

## Boundaries

- **Role:** the write-only editor of an existing SRD — apply changes one
  confirmed edit at a time. The counterpart to the read-only `review`.
- **Must not:** invent or restate rules — defer all format, style, logic, and
  rules to `create`'s reference files; edit metadata (Owners, Initiative,
  Designs), set back-links, or change `Status` — only flag those gaps
  (STR-2..7, STA-*). Acceptance stays a human decision. The only write to
  `<srd>.review.md` allowed is deleting a fully-fixed finding in feedback mode
  (see feedback); every other mode leaves the review file untouched.

## Sources of truth

The rules, checklist, procedures, template, and glossary live with `create`;
reuse them, never duplicate. **This skill depends on `../create/references/*`,
`../create/assets/*`, and `../create/scripts/*` — do not move or rename
`create`. If any referenced file is missing at run time, stop and tell the
user; do not proceed.** Read these before editing:

- [../create/references/srd-standard.md](../create/references/srd-standard.md)
  — the rules (`STR`, `STA`, `LANG`, `REQ`, `GLO`, `SCO`, `MD`, Quality
  Bar). Every edit and check defers to these ids.
- [../create/references/srd-checklist.md](../create/references/srd-checklist.md)
  — the action-neutral verification checklist; re-validation runs it.
- [../create/references/authoring-guide.md](../create/references/authoring-guide.md)
  — house extensions (US English, sub-numbering, terminology consistency, the
  consistency pass) and the Bad→Good defect classes to fix toward.
- [../create/references/srd-procedures.md](../create/references/srd-procedures.md)
  — shared operating procedures (glossary resolution).
- [../create/assets/srd-template.md](../create/assets/srd-template.md)
  — the required section order; consult it when restructuring.
- [../create/scripts/glossary-fingerprint.sh](../create/scripts/glossary-fingerprint.sh)
  — hashes the shared glossary so its term digest is rebuilt only on change; the
  digest keeps term edits linking, not redefining.

## Session start (every mode)

Before any edit:

1. **Read** the whole SRD top to bottom.
2. **Approval gate.** Read the `Status` metadata, pre-fill approved (`Accepted`)
   vs in-progress (anything else), then **show it and ask the user to confirm or
   override**. The answer governs id rules for the whole session — never trust
   `Status` silently.
3. **Glossary.** Run the glossary-resolution procedure in
   [../create/references/srd-procedures.md](../create/references/srd-procedures.md).

## Id rules

The approval gate decides what may happen to requirement / scope / glossary ids:

- **In-progress** — free to renumber a group after a split, merge, add, or
  remove, and to fix collisions or gaps (REQ-2/3/4). Update every cross-reference
  the change touches.
- **Approved** — **existing ids are frozen.** Additions only, via sub-numbering
  (`GR-1a`, `GR-1b`); never renumber or rename an existing id. If a real fix
  cannot be done without touching an existing id, **try add-only first**; if that
  is impossible, present the conflict and the trade-off and **leave it flagged**
  unless the user explicitly approves the id change.

Whenever any id must change, **state the change and get explicit approval** as
part of the one-change confirmation.

## Edit discipline

All interactive editing follows the same loop. Per change:

1. Propose **exactly one** change: its location/id, the problem (cite the rule
   id), the **before** and **after** text, and a one-line rationale.
2. Apply only on explicit approval. Never batch unrelated changes. Never edit
   without confirmation.
3. **Re-validate the affected entry + cross-refs** immediately against
   [../create/references/srd-checklist.md](../create/references/srd-checklist.md),
   focusing on the checks the edit can touch: scope coverage (SCO-2/3), id
   uniqueness/order (REQ-3/4), term use (GLO-3), and any requirement that
   references or is referenced by the edit. Report if the fix introduced a new
   problem.
4. At **session end**, run the full checklist plus the consistency pass in
   [../create/references/authoring-guide.md](../create/references/authoring-guide.md)
   over the whole document, and report what remains.

Write every edit to the LANG, MD, and REQ rules in
[../create/references/srd-standard.md](../create/references/srd-standard.md)
(US English and one term per concept per the authoring guide). When an edit
restructures sections, follow the order in
[../create/assets/srd-template.md](../create/assets/srd-template.md).

## Modes

Detect the mode from the user's words; the default is interactive.

- `edit path/to/srd.md` → **interactive** (default).
- `edit path/to/srd.md <path>.review.md` (or with pasted feedback) →
  **feedback**.
- `edit path/to/srd.md polish` → **polish**.
- `edit path/to/srd.md <id | "quoted text" | description>` → **targeted**.

### interactive (default)

1. Run the session-start steps.
2. **Front-load** a grouped issue summary — read the whole SRD and present every
   issue found, grouped by document section (Metadata, Introduction, Glossary,
   Scope, Requirements), each citing its rule id. Edit nothing yet.
3. **Walk entry by entry** in document order — each requirement (`PFX-n`), each
   glossary term, each scope item — applying the edit-discipline loop to every
   fix the user approves. Move to the next entry only after the current one is
   resolved or skipped.
4. Close with the full consistency pass and the chat summary.

### feedback

Apply findings from a review, deleting each finding as it is fully fixed.

1. Input is a `<srd>.review.md` path **or feedback pasted inline** (email,
   ticket, chat). Parse the findings from either.
2. Run the session-start steps.
3. Work findings in **severity order — blocker → major → minor** (use the
   review's tags; for untagged pasted feedback, judge severity from the rule).
4. For each finding, run the edit-discipline loop: propose the fix, apply on
   approval, re-validate. When the fix **fully** resolves a finding parsed from
   an on-disk `<srd>.review.md`, delete that finding from the file per
   "Review-file upkeep". A partial or declined fix leaves the finding untouched.
5. Close with the full consistency pass and the chat summary.

#### Review-file upkeep

Feedback mode only, and only for findings parsed from an on-disk
`<srd>.review.md` — pasted-inline feedback has no file to update. On each
**full** fix, in the edit-discipline loop right after apply + re-validate:

1. Delete the finding's bullet, with its indented continuation lines, from the
   review file.
2. If the file carries a summary or per-severity count line, re-tally it.
3. Bump the `Updated:` date to today.
4. Remove a section heading (Metadata, Introduction, Glossary, Scope,
   Requirements) once its last bullet is gone.
5. When the last finding is deleted, delete the whole `<srd>.review.md` file.

Deletion is the only edit — never strike through, annotate, or add findings; a
partial or declined fix leaves its finding in place.

### polish

Mechanical-only cleanup, still **confirm each** change (same loop). Scope is
limited to: 80-column wrap (MD-2), British → US spelling, identifier
format/order (REQ-2/3/4 — subject to the approval gate), keyword capitalization
(LANG-4), valid Markdown (MD-1), stray example/note text (REQ-7), spacing and
punctuation. Do not rewrite requirement meaning or restructure. Close with the
chat summary.

### targeted

Edit one entry the user points to — by **requirement id** (`GR-3a`), **quoted
text**, or **free description** ("the login timeout rule").

1. Run the session-start steps.
2. Locate the target. For quoted text or a description, **confirm the match**
   before editing.
3. Apply the edit-discipline loop to that entry.
4. **Always run a consistency check after** — the affected entry plus its
   cross-refs — and report whether the edit introduced any inconsistency.

## Deliverable

The skill **edits the source file in place**. It writes no other file, except
that feedback mode deletes fully-fixed findings from `<srd>.review.md` (see
"Review-file upkeep"). Close every session with an in-chat summary — a manifest
of approved edits, not a re-narration of diffs the user already saw:

- What changed: entry/id, one line each.
- What was flagged and left (frozen-id conflicts, metadata gaps, anything the
  user declined).
- Outstanding human follow-ups (placeholders, back-links, Status).

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.
