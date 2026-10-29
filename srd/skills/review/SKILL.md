---
name: review
description: >
  Reviews an existing Software Requirement Document (SRD) for consistency,
  logic, and conformance to the SRD standard, without editing it. Use when
  asked to review, audit, critique, or check an SRD, or to re-check whether
  prior review findings were fixed.
argument-hint: "<path to SRD> [walk | check [#n,n…] | errata | feedback]"
license: MIT
---

# review

## Usage

```
/review <srd>             review (default): resolve fixed + append new
/review <srd> walk        interactive, section by section
/review <srd> check       re-verify open findings against the current SRD
/review <srd> check #4,6  re-verify only findings #4 and #6
/review <srd> errata      re-sort existing findings into ## Errata
/review <srd> feedback    terse plain-text list of open tasks
```

Review an SRD someone else wrote and report what fails the SRD standard,
without editing it.

## Boundaries

- Role: the read-only reviewer of an SRD written by someone else. Produce
  findings; the author acts on them, one by one through `srd:edit` feedback
  mode — never a loop improvised here.
- Owns: the `<srd>.review.md` file beside the source — its creation,
  structure, numbering, and lifecycle — in every mode. No other skill writes
  it; `edit` never touches it.
- Must not: edit the source SRD or fix anything; restate or invent rules —
  defer all format, style, logic, and rules to `create`'s reference files.

## Sources of truth

The rules, checklist, and defect classes live with `create`; this skill reuses
them and never restates a rule. It depends on `../create/references/*` — do
not move or rename `create`. If a referenced file is missing at run time, stop
and tell the user.

- [../create/references/project-config.md](../create/references/project-config.md)
  (eager) — the gate every mode passes first, and the project paths,
  standard, and server it names.
- The SRD standard (fetched live per that file; every mode but `feedback`,
  which only lists findings already in the file) — the rules (`STR`, `STA`,
  `LANG`, `REQ`, `GLO`, `SCO`, Quality Bar). The review checks every rule.
- [../create/references/authoring-guide.md](../create/references/authoring-guide.md)
  (eager) — house additions (US English, sub-numbering, draft scaffolds,
  terminology consistency), the consistency pass, and the Bad→Good defect
  classes to recognize.
- [../create/references/errata.md](../create/references/errata.md) (on-demand:
  classifying a finding as errata) — the gate, allowlist, and exclusions of the
  bulk-fix errata class.
- [../create/assets/srd-template.md](../create/assets/srd-template.md)
  (on-demand: an errata finding on the STR-8 keyword notice, missing or wrong)
  — the one correct notice text `errata.md` names as its fix.
- [../create/references/doc-corpus.md](../create/references/doc-corpus.md)
  (on-demand: the facts-vs-corpus pass, which only `review` and `walk` run) —
  how to reach the documentation corpus, how its sources rank, and where an
  unconfirmed claim goes. `check` reads only the KB pages whose `srd_ref`
  names the SRD (check step 1); `errata` and `feedback` never reach it.
- [../create/references/srd-procedures.md](../create/references/srd-procedures.md)
  (on-demand: the first GLO-3, GLO-4, or STR-10 check) — the Company
  Glossary's term set, from the server.

Apply the full rule set. `create` leaves STR-2..7 (≥ 2 owners, Initiative
link, Designs link or `N/A` when no UI change) and STA-* (valid Status; not
`ACCEPTED` without an approved design or the Quality Bar) as placeholders; a
finished SRD under review must satisfy them — flag every gap. Exception: the
back-links (STR-4, STR-6) live in the external ticket and design tool, so check
only that the forward Initiative and Designs links are present and never raise
a back-link finding.

## Documentation corpus

Procedure, trust, and where an outcome goes: the shared corpus reference in
Sources of truth. `review` and `walk` run its draft check as their first step,
then invoke `srd:report-doc-gap` again after the closing line to offer the
drafts this run captured. They also run a facts-vs-corpus pass beside the rule
checks: for every requirement that asserts something about existing system
behavior ("the gateway retries 3×", "the API returns Y"), `search` the corpus
to confirm it. A claim the corpus contradicts is a `reference` finding; one it
cannot confirm is a doc gap for `srd:report-doc-gap`, never a finding in
`<srd>.review.md`. A KB section contradicting the SRD is a `reference` finding
too, never settled by `rank` (an SRD has none): it names both claims and both
fixes — align the SRD, or confirm its fact through `srd:edit` so `srd:kb`
rewrites the section — and calls neither side wrong. A finding resting on a
corpus result carries its source line
([Citing a source](../create/references/doc-corpus.md#citing-a-source)) on a
continuation line, whatever fixes it offers: it is the user's notice of the
source, so `fix-all` asks no second time about it.
`srd:kb` is not invoked: a review confirms no platform facts with the user.

## Severity and category

Tag every new finding with one severity (`blocker`, `major`, `minor`; never a
fourth) and one category — two only when it genuinely carries two — in one
bracket, severity first: `[major, logical, redundancy]`. The tiers, the
categories in precedence order, and how to place each defect are in
[references/finding-tags.md](references/finding-tags.md) (on-demand: before
the first finding `review` or `walk` writes).

## Modes

Every mode runs the gate in
[../create/references/project-config.md](../create/references/project-config.md)
first. The review file path is auto-derived, never passed as an argument. The
first token is the SRD path; the next selects the mode (default review when
omitted). Reserved words and `key=value` controls may appear anywhere; the
remaining tokens keep their documented order. With no arguments, ask which SRD
to review; fall back to the user's prose for free-form input.

- the SRD path only → review (default): read the whole SRD, write the review file.
- path + `walk` → walk: interactive, section by section; record only findings
  the user confirms.
- path + `check` → check: re-verify the review file's open findings against
  the current SRD; tick/move fixed ones, withdraw invalid ones. Trailing
  finding numbers scope it. Hunts no new defects.
- path + `errata` → errata: re-sort an existing review file so errata findings
  sit in `## Errata`. Reclassify only; hunts no new defects.
- path + `feedback` → feedback: emit a terse plain-text issue list of open
  tasks for an email or ticket. No file write.

A `key=value` that names no control here, or a word left over once the modes,
the target, and any text the skill takes are read: say it was not recognized,
name the ones that exist, and run with the defaults as if it were absent —
unless dropping it would widen what the run changes; then ask. A target that
resolves to nothing: say so and ask — never guess what to work on.

A file-writing run closes with one task-oriented line — e.g. "4 of 15 tasks
resolved, 2 withdrawn; 1 blocker still open." — plus the per-severity count of
open findings and whether a blocker stands between the SRD and the Quality Bar.
The findings live in the file the user is pointed to: the reply never lists
them — one per line, by group, or in a table — nor quotes their trigger text.
The one exception is `check`'s status table, which its procedure requires.
`errata` is a file-writing run and owes it too: its own "which numbers moved"
line says what the re-sort did, not what the file now holds.

Count those from the finished file, not from memory of writing it: a wrong
tally sends the author to the wrong findings.
In every mode, report tersely: no preamble or narration; state each fact once;
don't restate output the user can already see.

## Review file format

The layout, the global numbering, the citation form, and the section order
live in [references/review-file.md](references/review-file.md) — read it
before writing or updating a review file. Every mode that writes one needs it
in full.

## review (default)

1. Run the draft check; on a draft, `srd:report-doc-gap` drains what a prior
   session left unfiled — every draft filed, kept, or discarded — before any
   corpus search. Read the entire SRD top to bottom.
2. Check it against every rule in the standard, in document-section order,
   including the consistency pass and the house additions of the authoring
   guide. Also run the facts-vs-corpus pass
   ([Documentation corpus](#documentation-corpus)), handing each doc gap to
   `srd:report-doc-gap` on discovery.
3. If the review file does not exist, create it and write all findings with
   fresh numbers starting at `#1`, assigned in the document order of step 4,
   grouped and tagged as above.
4. If it exists, do not rewrite it. First resolve: re-verify open findings and
   tick+move each fixed one to `## Resolved` (a regression moves back, same
   number). Then append newly found defects with fresh numbers, assigned in
   document order (Metadata → Introduction → Glossary → Scope → Requirements,
   and by position within each), so two runs over the same defects number them
   the same way — errata to `## Errata`, the rest to their document section.
   Bump `updated:` only if something else in the file changed (review-file.md):
   a pass that resolves nothing and appends nothing writes nothing.
5. Close with the task-oriented line (Modes) and one start clause naming what
   the draft check found (`prior draft gaps: none`, or what was drained), unless
   a caller said it ran the check and so owns the clause. When the delegate
   makes the offer (below), pass that line and clause in its args as
   `closing: <text>` so its offer opens with them; otherwise write them as the
   reply.
   Then, unless a caller said it makes the closing offer, invoke
   `srd:report-doc-gap` to offer the drafts this run captured — and only then:
   the start check governs a *prior* session's drafts, this offer covers what
   *this* run captured, so a run that captured none invokes nothing here
   either. The offer is the delegate's, never written inline, so its
   file/change/drop choices reach the user.

## walk

Run the draft check as in review step 1, then go section by section
in document order. For each section:

1. Read it and identify every issue, including the facts-vs-corpus pass.
2. Present the findings — problem and fix for each. Record nothing yet.
3. Wait for the user to confirm which to keep (all, some, none).
4. Append only confirmed findings to the review file with fresh numbers,
   written as author-facing guidance. Create the file before the first write;
   bump `updated:` on each write, and a section where the user confirmed
   nothing produces no write at all.
5. Move on only after the user confirms or skips.

After the last section, close as in review step 5.

## check

Re-verify only — hunt no new defects. Withdrawal is check-only — no other mode
withdraws. The procedure — scoping by `#n,n`, judging each finding,
withdrawing, and the status-table close — is in
[references/check-mode.md](references/check-mode.md); read it when this mode
runs.

## errata

Re-sort an existing review file so its errata sit in `## Errata`. Reclassify
only — hunt no new defects. Keep every number. The procedure is in
[references/errata-mode.md](references/errata-mode.md); read it when this
mode runs.

## feedback

Emit plain text for an email or ticket — no file write: open findings only, in
the format of [references/feedback-mode.md](references/feedback-mode.md); read
it when this mode runs.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/srd/review.md` (pass `~` as is, the
file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable. A missing file needs no comment. On a correction or self-caught
mistake, append a one-line rule — general, naming nothing from the project at
hand (its files, tests, tickets) — to the sibling when this directory is
writable, else to the fallback, creating it, and report where.
