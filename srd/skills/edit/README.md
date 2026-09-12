# edit — Interactively Improve an SRD

Edits an existing Software Requirement Document (SRD) in place, one confirmed
change at a time, against the SRD standard — the write counterpart to the
read-only `review`.

## Usage

```
/edit path/to/srd.md                         interactive (default): front-load issues, then walk entry by entry
/edit path/to/srd.md 123                     interactive from line 123: resolve it to the nearest entry, walk from there
/edit path/to/srd.md path/to/srd.review.md   feedback: apply a review file or pasted feedback, blocker → major → minor
/edit path/to/srd.md #2                      feedback from finding #2, then next by number or jump to any number
/edit path/to/srd.md autofix                 bulk-apply the review's ## Errata block behind one confirmation
/edit path/to/srd.md polish                  mechanical-only cleanup (spelling, numbering, keywords), confirm each
/edit path/to/srd.md GR-3a                   targeted: edit one entry by id, quoted text, or description
```

## When to Use

- After `create` produces a draft and you want to tighten it.
- After `review` writes a `<srd>.review.md` and you want to apply the fixes.
- When a stakeholder sends loose feedback you want walked into the document.
- To clean up one requirement, or to do a quick mechanical pass before sign-off.

## How It Works

All format, style, logic, and rules come from `create`'s shared reference files
(`../create/references/*`, `../create/assets/*`, `../create/scripts/*`); this
skill cites them, never restates them. Do not move or rename `create`, or this
skill loses its standard.

### Session start (every mode)

1. Reads the SRD top to bottom.
2. Drains what a prior session left buffered for this SRD: unfiled doc gaps
   (`srd:report-doc-gap`) and unwritten platform facts (`srd:kb`), offering to
   work them now.
3. Approval gate: reads `Status`, pre-fills approved vs in-progress, and asks
   you to confirm or override. This governs id rules for the session.
4. Resolves the per-project glossary and loads its term digest, regenerating it
   only when the glossary changed.

`autofix` runs only steps 1–2: errata never touches ids or terms.

### Id rules

- In-progress SRD: free to renumber a group after split/merge/add/remove and
  fix collisions, updating cross-references.
- Approved SRD: existing ids are frozen — additions only, via sub-numbering
  (`GR-1a`, `GR-1b`). Any change to an existing id needs your explicit
  approval; otherwise the fix is offered add-only or left flagged.

### The edit loop

Every mode but `autofix` proposes one change at a time — location, rule id,
before/after, one-line rationale — and applies it only on your answer: `Y`
apply and stay on the entry, `YN` apply and move on, `S` skip, `E` apply your
amended text. After each edit it re-validates the entry and its cross-refs and
logs the change (below). Held-over questions go into a numbered
`## Open questions` list you answer by number, never as asides trailing a
proposal.

### Documentation corpus and knowledge base

When the platform documentation corpus (`srd-doc`) is reachable, an edit that
asserts existing system behavior is checked against it first; without a corpus
the skill edits offline. A claim the docs cannot confirm is handed to
`srd:report-doc-gap`; a fact the docs lack but you confirm is handed to
`srd:kb`. Both buffer silently — confirming a proposal that states the fact is
what attests it, so there is no separate "bank this?" prompt. At session end
`srd:kb` writes the attested facts and `srd:report-doc-gap` offers to work the
gaps it buffered.

### Decision log

Each applied edit is written straight to `<srd>.decisions.md` beside the source
— what changed and why, in prose an author can read without knowing the SRD
standard. Your own rationale is what gets recorded, tidied into clean sentences.

- Written after every edit, so nothing is lost if the session dies mid-flow.
- Accumulates across sessions: one file per SRD, newest session block first.
- Applied edits only — what you skipped or declined stays in `<srd>.review.md`.
- The newest block is the change summary to hand the author; the closing
  manifest points at it.

### Draft scaffolds

Two working scaffolds live in a draft SRD (defined in `create`'s authoring
guide); `edit` maintains both and flags them as blockers for `ACCEPTED`.

- In Scope `--- TODO ---` marker: In Scope derives from the requirements, so
  `### In Scope` may hold just this marker until the requirements settle. While
  it stands, `edit` suppresses In-Scope-coverage complaints (SCO-2) and will not
  invent scope items. When you signal the requirements are done (or ask to fill
  In Scope), it derives candidate `SC-n` items from the requirement groups and
  walks them point by point for you to keep, reword, merge, split, or drop,
  then replaces the marker.
- `## TODO` section: a numbered list of open issues to return to, kept as the
  last section. Say "Add X to TODO" at any time and `edit` appends it as the
  next item (no confirm loop — the instruction is the confirmation).

### What it will not do

- No metadata edits: never fills Owners/Initiative/Designs, sets back-links, or
  changes `Status`. It only flags those gaps. Acceptance stays a human call.
- No review-file writes: it edits the source only; `review` owns
  `<srd>.review.md` across all modes and `edit` never touches it.
- No silent edits: every change is confirmed; mechanical ones too.

## Modes

- Interactive (default), `/edit path/to/srd.md`: front-loads a grouped issue
  summary, then walks the SRD entry by entry — each requirement, glossary term,
  and scope item — through the edit loop. With a line number
  (`/edit path/to/srd.md 123`) it resolves the line to the entry or paragraph
  at or nearest it, skips the front-load, and walks from there to the end.
- Feedback, `/edit path/to/srd.md path/to/srd.review.md`: takes a
  `<srd>.review.md` from `review` or feedback pasted inline and works the
  findings blocker → major → minor through the edit loop. Never writes the
  review file; closes by pointing you to `review … check` to tick off what
  landed. With a finding number (`/edit path/to/srd.md #2`) it needs an
  existing review file, enters at that finding, then advances to the next by
  number or jumps to any number you name.
- Autofix, `/edit path/to/srd.md autofix`: applies the `## Errata` block of
  `<srd>.review.md` — the mechanical, meaning-preserving findings `review`
  recorded — behind a single batch confirmation, not the edit loop. Never
  re-scans the SRD. Each fix is an exact `old → new` substitution verified at
  its anchor before the write: it applies only where `old` matches exactly once
  inside the entry the finding names, and reports — rather than guesses —
  anything stale, ambiguous, or malformed. It never writes the review file;
  it hands off to `review … check` scoped to the applied errata numbers, so
  `review` moves just those into `## Resolved` and leaves other findings
  untouched.
- Polish, `/edit path/to/srd.md polish`: mechanical cleanup only (US spelling,
  identifier format, Markdown, keyword capitalization, stray example text),
  still confirming each change. No restructuring or meaning changes.
- Targeted, `/edit path/to/srd.md GR-3a`: edits a single entry, pointed to by
  requirement id, quoted text, or free description (it confirms the match
  first), and always re-validates the entry and its cross-refs afterward.

Every mode closes with a manifest: what changed (one line each), what was
flagged and left, outstanding human follow-ups, and the path to
`<srd>.decisions.md`.

## Related Skills

- `create` — author a new SRD to the same standard; owns the shared references.
- `review` — read-only review that produces the `<srd>.review.md` this skill
  consumes and reclassifies via `review … check`.
- `srd:report-doc-gap` — files the documentation gaps an edit exposes.
- `srd:kb` — writes the platform facts an edit attests into the knowledge base.

## Evaluations

**Scenario 1 — Interactive edit of a non-atomic requirement, approved SRD.**
Request: `/edit specs/login.md` where `Status: ACCEPTED` and `GR-3a` reads
"The system SHALL validate the token and log the attempt."
- Runs the approval gate first: reads `Status: ACCEPTED`, states it, and asks
  the user to confirm before editing. Resolves the glossary.
- Front-loads a grouped issue summary, then walks entry by entry; for `GR-3a`
  proposes one change — split into two atomic rules (REQ-1) — with location,
  before/after, and rationale.
- Because ids are frozen, does the split add-only via sub-numbering (e.g. keeps
  `GR-3a`, adds `GR-3b`) rather than renumbering; if that is impossible, flags
  the conflict and waits for explicit id-change approval.
- Applies nothing until approved; re-validates the affected entry and
  cross-refs after the edit.

**Scenario 2 — Apply a review feedback file.**
Request: `/edit specs/login.md specs/login.review.md`.
- Parses findings from the review file and works them blocker → major → minor.
- Fixes each interactively (one change, confirm, re-validate), referencing
  findings by number; leaves `login.review.md` untouched.
- Closes by telling the user to run `review specs/login.md check` to tick off
  what landed and reclassify the rest, plus the manifest of what changed and
  what was left flagged.

**Scenario 3 — Targeted edit by description.**
Request: `/edit specs/login.md fix the vague "fast" requirement`.
- Locates the matching requirement and confirms the match before editing.
- Proposes a concrete, verifiable replacement (e.g. a measurable threshold) per
  REQ-5/6, with before/after.
- After applying, re-validates that entry plus its cross-references and reports
  whether anything new broke.

**Scenario 4 — Polish pass leaves metadata and meaning untouched.**
Request: `/edit specs/login.md polish` on an in-progress draft.
- Confirms each mechanical fix (British → US spelling, keyword caps, stray
  example text) — applies none silently.
- Does not rewrite requirement meaning, restructure, fill Owners/Initiative/
  Designs, or change `Status`; flags those gaps instead.
- Closes with the manifest of the mechanical changes made.

**Scenario 5 — Terse output.**
Request: `/edit specs/login.md`.
- No preamble or narration; each proposal opens with the change itself
  (location, before/after, rule id).
- The closing manifest lists approved edits one line each — not a re-narration
  of diffs the user already saw — and points at `<srd>.decisions.md` instead of
  re-printing its contents.

**Scenario 6 — Generate In Scope from settled requirements.**
Request: `/edit specs/login.md`, then partway through: "the requirements are
final now — fill in the In Scope."
- Before the signal, `### In Scope` holds only `--- TODO ---`; `edit` never
  flags SCO-2 against it and never fabricates scope items.
- On the signal, derives candidate `SC-n` items from the requirement groups and
  walks them point by point (confirm/edit each), then replaces the marker with
  the confirmed items and re-runs the SCO-2/3 coverage check.

**Scenario 7 — Add to TODO on demand.**
Request: mid-session, "Add: confirm the lockout threshold with security to
TODO."
- Appends it as the next numbered item in the `## TODO` section (creating the
  section as the last one if absent), without the propose-and-confirm loop.
- Renumbers nothing else; reports only the single line added. At session end
  the non-empty `## TODO` is flagged as a follow-up that blocks `ACCEPTED`.

**Scenario 8 — Autofix bulk-applies the Errata block.**
Request: `/edit specs/login.md autofix` with a `specs/login.review.md` whose
`## Errata` block holds three findings.
- Reads only the `## Errata` block — does not re-scan the SRD for new mechanical
  issues; skips the approval gate and glossary resolution.
- Lists the three substitutions and takes one confirmation for the whole batch,
  not the per-change loop; on approval verifies each `old` at its anchor and
  applies the two that match exactly once, reporting the third as stale because
  its anchor no longer contains the quoted text.
- Does not write `login.review.md` itself; hands off to `review specs/login.md
  check #n #n` scoped to the two applied errata, which ticks them into
  `## Resolved`. Closes with a manifest naming what was applied, reclassified,
  and skipped.

**Scenario 9 — Interactive from a line-number start point.**
Request: `/edit specs/login.md 210`.
- Runs session start, then resolves line 210 to the entry or paragraph at or
  nearest it (e.g. `GR-4b`) instead of front-loading a whole-document summary.
- Begins the entry-by-entry walk there and continues in document order to the
  end; the closing consistency pass still covers the whole document.

**Scenario 10 — Feedback from a `#n` start point with jump navigation.**
Request: `/edit specs/login.md #2` with an existing `specs/login.review.md`.
- Enters at finding #2 (not severity order); if the review file is absent, says
  so and stops.
- After each finding is resolved or skipped, defaults to the next finding by
  number, or jumps to any number the user names. Leaves the review file
  untouched and closes by pointing to `review specs/login.md check`.

**Scenario 11 — Corpus-grounded edit routes what the docs cannot confirm.**
Request: `/edit specs/login.md GR-2` with the `srd-doc` corpus reachable; the
user wants `GR-2` to say the gateway retries a failed token check three times.
- Searches the corpus before accepting the edit; the retry count appears in no
  document, so the gap is buffered with `srd:report-doc-gap` silently — no
  interruption, no grill mid-edit.
- The proposal states the retry count as a fact; the user's `Y` attests it, so
  `srd:kb` buffers it too. No separate "bank this?" question is asked.
- At session end `srd:kb` writes the fact and reports a one-line pointer;
  `srd:report-doc-gap` offers to work the buffered gap and respects a defer.

**Scenario 12 — Session start drains what a prior session left.**
Request: `/edit specs/login.md` after a session cleared with two unfiled doc
gaps and one unwritten platform fact buffered for this SRD.
- Before the approval gate, surfaces the counts and topics from both delegates
  and offers to work them now.
- On defer, proceeds straight to the approval gate; both buffers stay intact for
  the next start.

**Scenario 13 — Decision log written per edit.**
Request: `/edit specs/login.md`; the user answers `Y` to one proposal with the
reason "retention isn't ours, drop it", then `S` to the next.
- Appends the applied change to `specs/login.decisions.md` before proposing the
  next one; creates the file with `cfsync-plugin: ignore-push` front matter on
  the first write.
- Records the entry, the change in prose, and the user's reason tidied into a
  clean sentence — never a diff, never an invented rationale.
- The skipped proposal is not logged; the closing manifest points at the file's
  newest session block as the author's summary.
