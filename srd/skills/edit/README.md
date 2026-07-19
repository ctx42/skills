# edit — Interactively Improve an SRD

Edits an existing Software Requirement Document in place, one confirmed change at
a time, against the SRD standard (reused from `create`). The write
counterpart to the read-only `review`.

All format, style, logic, and rules come from `create`'s shared reference
files (`../create/references/*`, `../create/assets/*`,
`../create/scripts/*`); this skill cites them, never restates them. Do not move
or rename `create`, or this skill loses its standard.

## Modes

- **Interactive (default)**: `/edit path/to/srd.md`
    - Reads the whole SRD, front-loads a grouped issue summary, then walks it
      entry by entry — each requirement, glossary term, and scope item —
      proposing one change at a time with before/after and rationale, applying
      only on approval, and re-validating after each.

- **Feedback (review-driven)**: `/edit path/to/srd.md path/to/srd.review.md`
    - Takes a `<srd>.review.md` from `review` **or feedback pasted inline**.
      Works findings blocker → major → minor, fixing each interactively.
    - Never writes the review file — `review` owns it across all modes. Re-run
      `review … check` afterward to tick off what landed and reclassify the
      rest.

- **Polish (quick mechanical pass)**: `/edit path/to/srd.md polish`
    - Mechanical cleanup only (wrapping, US spelling, numbering format, markdown,
      keyword caps, stray examples), still confirming each change. No
      restructuring or meaning changes.

- **Targeted (one entry)**: `/edit path/to/srd.md GR-3a`
    - Edits a single entry, pointed to by requirement id, quoted text, or free
      description (it confirms the match first). Always runs a consistency check
      after the edit.

## Session Start (every mode)

1. Reads the SRD top to bottom.
2. **Approval gate** — reads `Status`, pre-fills approved vs in-progress, and
   asks you to confirm or override. This governs id rules for the session.
3. Resolves the per-project glossary and loads its term digest, regenerating it
   only when the glossary changed.

## Id Rules

- **In-progress** SRD — free to renumber a group after split/merge/add/remove
  and fix collisions, updating cross-references.
- **Approved** SRD — existing ids are **frozen**: additions only, via
  sub-numbering (`GR-1a`, `GR-1b`). Any change to an existing id needs your
  explicit approval; otherwise the fix is offered add-only or left flagged.

## What It Will Not Do

- **No metadata edits** — never fills Owners/Initiative/Designs, sets back-links,
  or changes `Status`. It only flags those gaps. Acceptance stays a human call.
- **No review-file writes** — it edits the source only; `review` owns
  `<srd>.review.md` across all modes and `edit` never touches it.
- **No silent edits** — every change is confirmed; mechanical ones too.

## Draft Scaffolds

Two working scaffolds live in a draft SRD (defined in `create`'s authoring
guide); `edit` maintains both and flags them as blockers for `Accepted`.

- **In Scope `--- TODO ---` marker** — In Scope derives from the requirements, so
  `### In Scope` may hold just this marker until the requirements settle. While
  it stands, `edit` suppresses In-Scope-coverage complaints (SCO-2) and will not
  invent scope items. When you signal the requirements are done (or ask to fill
  In Scope), it derives candidate `SC-n` items from the requirement groups and
  walks them **point by point** for you to keep, reword, merge, split, or drop,
  then replaces the marker.
- **`## TODO` section** — a numbered list of open issues to return to, kept as
  the last section. Say **"Add X to TODO"** at any time and `edit` appends it as
  the next item (no confirm loop — the instruction is the confirmation).

## When to Use

- After `create` produces a draft and you want to tighten it.
- After `review` writes a `<srd>.review.md` and you want to apply the fixes.
- When a stakeholder sends loose feedback you want walked into the document.
- To clean up one requirement, or to do a quick mechanical pass before sign-off.

## Related Skills

- `create` — author a new SRD to the same standard.
- `review` — read-only review that produces the `<srd>.review.md` this skill
  consumes.

## Evaluations

**Scenario 1 — Interactive edit of a non-atomic requirement on an approved SRD.**
Request: `/edit specs/login.md` where `Status: Accepted` and `GR-3a` reads
"The system SHALL validate the token and log the attempt."
- Runs the approval gate first: reads `Status: Accepted`, states it, and asks the
  user to confirm before editing. Resolves the glossary.
- Front-loads a grouped issue summary, then walks entry by entry; for `GR-3a`
  proposes **one** change — split into two atomic rules (REQ-1) — with location,
  before/after, and rationale.
- Because ids are frozen, does the split **add-only** via sub-numbering (e.g.
  keeps `GR-3a`, adds `GR-3b`) rather than renumbering; if that is impossible,
  flags the conflict and waits for explicit id-change approval.
- Applies nothing until approved; re-validates the affected entry and
  cross-refs after the edit.

**Scenario 2 — Apply a review feedback file.**
Request: `/edit specs/login.md specs/login.review.md`.
- Parses findings from the review file and works them **blocker → major →
  minor**.
- Fixes each interactively (one change, confirm, re-validate), referencing
  findings by number; leaves `login.review.md` untouched.
- Closes by telling the user to run `review specs/login.md check` to tick off
  what landed and reclassify the rest, plus an in-chat summary of what changed
  and what was left flagged.

**Scenario 3 — Targeted edit by description.**
Request: `/edit specs/login.md fix the vague "fast" requirement`.
- Locates the matching requirement and **confirms the match** before editing.
- Proposes a concrete, verifiable replacement (e.g. a measurable threshold) per
  REQ-5/6, with before/after.
- After applying, **always runs a consistency check** on that entry plus its
  cross-references and reports whether anything new broke.

**Scenario 4 — Polish pass leaves metadata and meaning untouched.**
Request: `/edit specs/login.md polish` on an in-progress draft.
- Confirms each mechanical fix (80-column wrap, British→US spelling, keyword
  caps, stray example text) — applies none silently.
- Does not rewrite requirement meaning, restructure, fill Owners/Initiative/
  Designs, or change `Status`; flags those gaps instead.
- Closes with an in-chat summary of the mechanical changes made.

**Scenario 5 — Terse output.**
Request: `/edit specs/login.md`.
- No preamble or narration; each proposal opens with the change itself
  (location, before/after, rule id).
- The closing summary is a manifest of approved edits — one line each — not a
  re-narration of diffs the user already saw.

**Scenario 6 — Generate In Scope from settled requirements.**
Request: `/edit specs/login.md`, then partway through: "the requirements are
final now — fill in the In Scope."
- Before the signal, `### In Scope` holds only `--- TODO ---`; `edit` never
  flags SCO-2 against it and never fabricates scope items.
- On the signal, derives candidate `SC-n` items from the requirement groups and
  walks them **point by point** (confirm/edit each), then replaces the marker
  with the confirmed items and re-runs the SCO-2/3 coverage check.

**Scenario 7 — Add to TODO on demand.**
Request: mid-session, "Add: confirm the lockout threshold with security to
TODO."
- Appends it as the next numbered item in the `## TODO` section (creating the
  section as the last one if absent), without the propose-and-confirm loop.
- Renumbers nothing else; reports only the single line added. At session end the
  non-empty `## TODO` is flagged as a follow-up that blocks `Accepted`.
