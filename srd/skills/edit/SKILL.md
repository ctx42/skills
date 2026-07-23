---
name: edit
description: >
  Improves an existing Software Requirement Document (SRD) by editing it in
  place against the SRD standard. Use when asked to edit, improve, fix,
  revise, or clean up an SRD, or to apply findings from a review file or
  pasted feedback.
argument-hint: "<path to SRD> [review-file | polish | target]"
license: MIT
---

# edit

Drive an existing SRD toward the SRD standard by editing the source in place.

## Boundaries

The write-only editor of an existing SRD, applying changes one confirmed edit
at a time — the counterpart to the read-only `review`. It must not invent or
restate rules (defer all format, style, logic, and rules to `create`'s
reference files), nor edit metadata (Owners, Initiative, Designs), set
back-links, or change `Status` — only flag those gaps (STR-2/3/5/7, STA-*).
The back-links (STR-4/6) are external, so it checks the forward Initiative and
Designs links are present and never flags a back-link gap.
Acceptance stays a human decision. It maintains the two draft scaffolds — the In
Scope `--- TODO ---` marker and the `## TODO` section (see
[Draft scaffolds](#draft-scaffolds)) — but resolves them only on the user's
signal, never silently, and flags both as acceptance blockers. It never writes
`<srd>.review.md` — `review` owns that file across all modes; `edit` only reads
it.

## Sources of truth

The rules, checklist, procedures, template, and glossary live with `create`;
reuse them, never duplicate. **This skill depends on `../create/references/*`,
`../create/assets/*`, and `../create/scripts/*` — do not move or rename
`create`. If any referenced file is missing at run time, stop and tell the
user; do not proceed.** Read these before editing:

- [../create/references/srd-standard.md](../create/references/srd-standard.md)
  (eager) — the rules (`STR`, `STA`, `LANG`, `REQ`, `GLO`, `SCO`, `MD`,
  Quality Bar). Every edit and check defers to these ids; re-validation
  checks against them directly.
- [../create/references/authoring-guide.md](../create/references/authoring-guide.md)
  (eager) — house extensions (US English, sub-numbering, terminology
  consistency, the consistency pass) and the Bad→Good defect classes to fix
  toward.
- [../create/references/srd-procedures.md](../create/references/srd-procedures.md)
  (on-demand: session start for glossary; In Scope generation for the derivation
  procedure) — shared operating procedures (glossary resolution; deriving In
  Scope from the settled requirements).
- [../create/assets/srd-template.md](../create/assets/srd-template.md)
  (on-demand: restructuring) — the required section order.
- [../create/scripts/glossary-fingerprint.sh](../create/scripts/glossary-fingerprint.sh)
  (run, not read) — hashes the shared glossary so its term digest is rebuilt
  only on change; the digest keeps term edits linking, not redefining.

## Documentation corpus (when available)

Some setups expose the platform's live documentation over the `srd-doc` MCP
server — the read tools `mcp__srd-doc__search` (query + optional `k`),
`mcp__srd-doc__get_doc` (document id), and `mcp__srd-doc__list_docs` (no args).
When a new or changed requirement asserts something about existing system
behaviour, `search` the corpus to confirm it before accepting the edit. Degrade
MCP → the `srd-doc` REST mirror
(`curl 'http://<host>:7777/search?q=TEXT&k=5'`, `.../docs/<id>`) → scoped
Grep/Read over a local corpus checkout, falling through only when a step
genuinely is not there. Absent a corpus, edit offline as before.

### Reporting a doc gap

When the corpus **cannot confirm** such a claim — missing, wrong, incomplete, or
ambiguous docs — that is a *documentation* gap, not an SRD defect. Hand it to
`srd:report-doc-gap`, which owns capture, the grill, and the confirmed filing;
invoke it on discovery — it buffers the gap without interrupting the edit — and
at session start, where it drains any gaps left unfiled. Editing the SRD text
stays this skill's job; only corpus deficiencies cross to `report-doc-gap`.

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
2. Close each proposal by offering the choices **(Yes / Yes Next / Skip /
   Edit)** — the capital letter is the key — and apply only on explicit
   approval, reading the verb:
   - `Y` (Yes) — apply this change, then **stay on the current entry** and
     propose its next issue; advance only once the entry is exhausted.
   - `YN` (Yes Next) — apply this change and **move on to the next entry**,
     leaving any remaining issues on this one flagged.
   - `S` (Skip) — change nothing; leave the issue flagged.
   - `E` (Edit) — apply the user's amended text in place of the proposal.
   Never batch unrelated changes. Never edit without confirmation.
3. **Re-validate the affected entry + cross-refs** immediately against the
   rules in
   [../create/references/srd-standard.md](../create/references/srd-standard.md),
   focusing on the checks the edit can touch: scope coverage (SCO-2/3 —
   suspended while the In Scope `--- TODO ---` marker stands, see
   [Draft scaffolds](#draft-scaffolds)), id
   uniqueness/order (REQ-3/4), term use (GLO-3), and any requirement that
   references or is referenced by the edit. Report if the fix introduced a new
   problem. When the edit asserts a claim about existing system behaviour and a
   corpus is available, confirm it against the docs (see
   [Documentation corpus](#documentation-corpus-when-available)) and delegate
   any doc gap to `srd:report-doc-gap`.
4. At **session end**, re-check the whole document against every rule in the
   standard plus the consistency pass in
   [../create/references/authoring-guide.md](../create/references/authoring-guide.md),
   and report what remains.

Write every edit to the LANG, MD, and REQ rules in
[../create/references/srd-standard.md](../create/references/srd-standard.md)
(US English and one term per concept per the authoring guide). When an edit
restructures sections, follow the order in
[../create/assets/srd-template.md](../create/assets/srd-template.md).

## Draft scaffolds

Two working scaffolds live in a draft SRD (see the House additions in
[../create/references/authoring-guide.md](../create/references/authoring-guide.md)).
Recognize and maintain them across every mode; never remove either silently, and
flag both at session end as human follow-ups that block `Accepted`:

- In Scope `--- TODO ---` marker — while `### In Scope` holds only this marker,
  In Scope is knowingly pending: suppress every SCO-2 / In-Scope-coverage
  complaint everywhere (the front-loaded issue summary, re-validation, and the
  consistency pass), and do not fabricate `SC-n` items early. Resolve it only via
  the generation step below.
- `## TODO` section — a numbered list of open issues the human must return to,
  kept as the document's last section.

### Add to TODO (any time)

When the user says "Add X to TODO" (or similar) at any point in the session,
append X as the next numbered item in the `## TODO` section — creating the
section as the last section if it is absent. The instruction is itself the
confirmation, so apply it without the propose-and-confirm loop; renumber nothing
else and report only the one line added.

### Generate In Scope (on the user's signal)

Only when the In Scope marker is present **and** the user signals the
requirements are complete (or asks to fill In Scope): run the In Scope
derivation procedure in
[../create/references/srd-procedures.md](../create/references/srd-procedures.md)
and walk its candidate `SC-n` items point by point through the edit-discipline
loop, applying each confirmed item. Replace the marker with the confirmed items,
then re-run the In-Scope-coverage check (SCO-2/3) now that it applies again. Do
not trigger this on your own — never derive In Scope while the user is still
shaping requirements.

## Modes

`$1` is the SRD path; `$2` selects the mode (interactive when omitted). With no
`$ARGUMENTS`, ask which SRD to edit; fall back to the user's prose for free-form
input.

- `$1` only → **interactive** (default).
- `$1` + a `<path>.review.md` (or pasted feedback) → **feedback**.
- `$1` + `polish` → **polish**.
- `$1` + `<id | "quoted text" | description>` → **targeted**.

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

Apply findings from a review. **Never write the review file** — `review` owns
it. After editing, tell the user to run `review <srd> check` to reclassify
what landed.

1. Input is a `<srd>.review.md` path **or feedback pasted inline** (email,
   ticket, chat). Parse the findings from either.
2. Run the session-start steps.
3. Work findings in **severity order — blocker → major → minor** (use the
   review's tags and finding numbers; for untagged pasted feedback, judge
   severity from the rule).
4. For each finding, run the edit-discipline loop: propose the fix, apply on
   approval, re-validate. Reference findings by their number in the chat
   summary; leave the review file untouched regardless of outcome.
5. Close with the full consistency pass and the chat summary, then point the
   user to `review <srd> check`.

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

Close every session with an in-chat summary — a manifest of approved edits, not
a re-narration of diffs the user already saw:

- What changed: entry/id, one line each.
- What was flagged and left (frozen-id conflicts, metadata gaps, anything the
  user declined).
- Outstanding human follow-ups (placeholders, back-links, Status), including an
  unresolved In Scope `--- TODO ---` marker and any non-empty `## TODO` section
  — both block `Accepted`.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/srd/edit.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
