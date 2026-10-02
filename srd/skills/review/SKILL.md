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
  findings; the author acts on them.
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
- [../create/references/doc-corpus.md](../create/references/doc-corpus.md)
  (on-demand: the facts-vs-corpus pass, which only `review` and `walk` run) —
  how to reach the documentation corpus, how its sources rank, and where an
  unconfirmed claim goes. `check`, `errata`, and `feedback` never reach it.
- [../create/references/srd-procedures.md](../create/references/srd-procedures.md)
  (on-demand: the first GLO-3 / STR-10 check) — the Company Glossary's term
  set, from the server.

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
to confirm it. A
claim the corpus contradicts is a `reference` finding; one it cannot confirm is
a doc gap for `srd:report-doc-gap`, never a finding in `<srd>.review.md`.
`srd:kb` is not invoked: a review confirms no platform facts with the user.

## Severity

Tag each finding:

- `blocker` — breaks Quality-Bar acceptance: non-atomic (REQ-1), unverifiable
  (REQ-5/6), uncovered In Scope item (SCO-2; suspended while the In Scope
  `--- TODO ---` marker stands), requirement contradicting Out of Scope
  (SCO-3), undefined term (GLO-3/STR-10), rule hidden in a glossary entry or
  metadata (GLO-1/2), duplicate or out-of-order id (REQ-3/4), missing forward
  link (STR-2/3/5/7), a missing or altered RFC 2119 / RFC 8174 keyword notice
  (STR-8), invalid or over-claimed Status (STA-*), an unresolved
  draft scaffold — the In Scope `--- TODO ---` marker or a non-empty `## TODO`
  section (house additions).
- `major` — real defect, does not block: style (LANG-1/2/5/6/7), terminology
  drift, overlapping or duplicate requirements, a normative keyword in the
  wrong case or the wrong section (LANG-3/4), and any `reference` finding —
  a wrong link, ticket id, or claim about the live system — since a reader
  acting on it is misled without the SRD being unacceptable.
- `minor` — cosmetic: British spelling, spacing, punctuation.

The rows are the common cases — STR-9/11-13, STA-4-8 and REQ-2/7/8 have
none. Place an unlisted rule by what breaking it costs: the Quality Bar
(blocker), a reader who must still act (major), the eye alone (minor). Say
which tier and why, so the next run lands in the same place. Never a fourth.

## Category

Also tag each finding with one category — two only when it genuinely carries
two — inside the same bracket as the severity, comma-separated, severity first
and the primary category next: `[major, logical, redundancy]`. Lowercase,
mandatory on every finding in every section, never a third category. One
bracket only: adjacent `][` is CommonMark reference-link syntax and renders as
a broken link in Obsidian.

Categories in precedence order — when a finding fits more than one, the higher
entry leads and the lower becomes the second tag:

- `structure` — a required part of the document is absent or malformed, or its
  lifecycle state is invalid (STR-*, STA-*).
- `logical` — two rules conflict, a case no rule covers, precedence between
  rules unstated.
- `coverage` — an In Scope item no requirement covers, a requirement
  contradicting Out of Scope, or a rule stated where rules do not live: a
  glossary entry, the metadata, a Note, the Introduction (SCO-2, SCO-3,
  GLO-1/2).
- `reference` — a link, ticket id, or claim about the live system that is
  wrong or stale. The standard forbids no such error, so this finding cites
  evidence where others cite a rule: the corpus doc id and heading that
  contradict it, or the dead link.
- `redundancy` — two rules state the same thing, or one subsumes the other.
- `verifiability` — a vague quality, an unmeasurable criterion, an open-ended
  list (REQ-5, REQ-6, LANG-7).
- `atomicity` — one item carrying more than one rule, an example or note
  inside a rule, a rule stating appearance instead of behavior (REQ-1, REQ-7,
  LANG-5, SCO-1).
- `terminology` — one concept under many names, an undefined term, casing that
  drifts from the glossary (GLO-3). A rule *hidden* in a glossary entry is
  `coverage`, not this: the defect is a requirement in the wrong place, not a
  word in the wrong form.
- `linguistic` — grammar, spelling, a missing word, the wrong subject or
  voice, a misplaced or lowercase normative keyword (LANG-1, LANG-2, LANG-3,
  LANG-4, LANG-6).
- `format` — markup, bold identifiers, id numbering, punctuation, spacing
  (REQ-2, REQ-3, REQ-4, REQ-8).

`reference` covers a wrong pointer or fact, `terminology` a diverging word
choice: an SRD that renames an existing platform concept is `terminology`.
Category is orthogonal to `## Errata`: an errata finding is `format` or
`linguistic` — or `structure` for the STR-8 notice, the one boilerplate the
allowlist admits — but not every `format` or `linguistic` finding is errata. A
normative keyword in the Introduction is `coverage` when its sentence states a
rule, `linguistic` (LANG-3) when it does not. A duplicate id's fix in an
`ACCEPTED` SRD gives the later item a fresh id and renumbers nothing (STA-7).

## Modes

Every mode runs the gate in
[../create/references/project-config.md](../create/references/project-config.md)
first. The review file path is auto-derived, never passed as an argument. The
first token is the SRD path; the next selects the mode (default review when
omitted). With no arguments, ask which SRD to review; fall back to the user's
prose for free-form input.

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

A file-writing run closes with one task-oriented line — e.g. "4 of 15 tasks
resolved, 2 withdrawn; 1 blocker still open." — plus the per-severity count of
open findings and whether a blocker stands between the SRD and the Quality Bar.
`errata` is a file-writing run and owes it too: its own "which numbers moved"
line says what the re-sort did, not what the file now holds, and the two answer
different questions.

Count those from the finished file, not from memory of writing it: a wrong
tally sends the author to the wrong findings, and it is the one number nobody
re-derives.
In every mode, report tersely: no preamble or narration; state each fact once;
don't restate output the user can already see.

## Review file format

The layout, the global numbering, the citation form, and the section order
live in [references/review-file.md](references/review-file.md) — read it
before writing or updating a review file. Every mode that writes one needs it
in full, so it is not summarized here.

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
   the draft check found (`draft gaps: none`, or what was drained), unless a
   caller said it ran the check and so owns the clause — a check that found
   nothing otherwise looks like one that never ran. Then, unless a caller said
   it makes the closing offer, invoke `srd:report-doc-gap` to offer the drafts
   this run captured — and only then:
   the start check governs a *prior* session's drafts, this offer covers what
   *this* run captured, so a run that captured none invokes nothing here either.

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

Re-verify only — hunt no new defects. Keep every number; bump `updated:` only
if something else in the file changed (review-file.md).

Trailing finding numbers scope the pass to those findings; the rest stay
untouched. Accept them comma- or space-separated, `#` optional — `check #4,6`,
`check #4 #6`, `check 4,6` all name #4 and #6. Report any listed number that is
absent or already resolved/withdrawn, and check the rest. Omitted, check every
open finding.

1. Judge each finding in scope against the current text:
   - fixed → tick `[x]` and move to `## Resolved`.
   - partial → stays `[ ]` in its section with `*(Partial — …)*` appended;
     never ticks.
   - not addressed → stays `[ ]`, untouched.
2. Withdrawal is check-only: a finding that proves invalid (mistaken, the
   author justified the text, or it cites a rule absent from the standard such
   as a defunct `MD-*`) moves to `## Withdrawn` with a reason. Never carry a
   non-enforceable finding open. No other mode withdraws — which is why this
   mode is where another skill's invalidity report lands: `srd:system-check`
   cannot write the review file, so it names the numbers its corpus lookups
   disproved and the user runs `check #n…` over them. Re-verify such a number
   like any other and withdraw it on the evidence, never on the report alone.
3. Close with both, in this order: the status table — number, current state,
   assessment — then the task-oriented line (Modes) beneath it. The table says
   what this pass did to each finding; the line says where the SRD now stands.
   Neither replaces the other.

## errata

Re-sort an existing review file so its errata sit in `## Errata`. Reclassify
only — hunt no new defects. Keep every number. Bump `updated:` when something
moved; a run that changes nothing writes nothing, or the pass is not idempotent
and a second run is indistinguishable from a first.

Rewriting a prose fix into the substitution shape needs the SRD's current text
to quote `old` exactly, so this mode reads the SRD as well as the review file.
It still edits only the review file.

1. Test each open finding against the gate and allowlist in
   [../create/references/errata.md](../create/references/errata.md). One that
   qualifies and is not yet under `## Errata` moves there keeping its number,
   `[minor]` tag, category, and citation; create the section at the top if
   absent. Classify conservatively: leave ambiguous findings where they are. A
   qualifying finding written as prose ("fix the spelling") is rewritten into
   the substitution shape as it moves. One finding naming several different
   fixes is split into one finding per substitution: each qualifying one moves
   to `## Errata` under a new number, while anything failing the gate stays
   under the original number, rewritten to name only the sites left; when
   every part qualifies, the original number goes with the first substitution.
   Report each split (the defects were already recorded, so this is not
   hunting).
2. Leave every other finding untouched, and drop any document section the move
   left with no open findings — `review-file.md` omits an empty section, and a
   heading left standing would move on the next run. The pass is idempotent.
3. If the review file does not exist, fall through to a normal review.
4. Report which numbers moved ("moved #4, #6, #9 to Errata"); say so when none
   moved.

## feedback

Emit plain text for an email or ticket — no file write:

- Title: `<Document Title> — Review Feedback`.
- Group by section name as a plain heading (no markdown symbols). `## Errata`
  is one such group — list it first, as `Errata`, when it holds open findings.
  An errata finding keeps its substitution in prose, not markdown:
  `#4 GR-2: "behaviour" should read "behavior"`.
- One bullet per open finding, blank-line separated. Keep the finding number
  and the SRD's own requirement id (`#7 GR-3a:`), then a one-line
  problem-and-fix. A finding against text with no id of its own — a metadata
  field, an Introduction sentence — is anchored the way the review file anchors
  it: the section name, and a short quote when the section holds more than one
  candidate. `#2 Metadata (Owners): only one owner is listed; add a secondary
  owner.` `#5 Introduction ("the system handles all remaining cases"): states a
  rule outside Requirements; move it or drop it.` Drop the checkbox, the
  severity tag, the category tag, and the rule-id citation. No bold. One
  bullet is one paragraph — it wraps like any prose, and "no multi-line
  bullets" means no sub-bullets and no blank line inside a bullet, not a
  bullet that fits on one physical line.
- Open findings only — omit Resolved and Withdrawn.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/srd/review.md`, the
sibling winning a conflict — a read-only install writes the second, and what it
learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule to the sibling when this directory
is writable, else to the fallback, creating it, and report where.