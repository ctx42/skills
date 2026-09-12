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

- [../create/references/srd-standard.md](../create/references/srd-standard.md)
  (eager) — the rules (`STR`, `STA`, `LANG`, `REQ`, `GLO`, `SCO`, Quality
  Bar). The review checks every rule.
- [../create/references/authoring-guide.md](../create/references/authoring-guide.md)
  (eager) — house additions (US English, sub-numbering, draft scaffolds,
  terminology consistency), the consistency pass, and the Bad→Good defect
  classes to recognize.
- [../create/references/errata.md](../create/references/errata.md) (on-demand:
  classifying a finding as errata) — the gate, allowlist, and exclusions of the
  bulk-fix errata class.
- [../create/references/doc-corpus.md](../create/references/doc-corpus.md)
  (eager) — how to reach the documentation corpus, how its sources rank, and
  where an unconfirmed claim goes.

Apply the full rule set. `create` leaves STR-2..7 (≥ 2 owners, Initiative
link, Designs link or `N/A` when no UI change) and STA-* (valid Status; not
`ACCEPTED` without an approved design or the Quality Bar) as placeholders; a
finished SRD under review must satisfy them — flag every gap. Exception: the
back-links (STR-4, STR-6) live in the external ticket and design tool, so check
only that the forward Initiative and Designs links are present and never raise
a back-link finding.

## Documentation corpus

Procedure, trust, and where an outcome goes: the shared corpus reference in
Sources of truth. `review` and `walk` invoke `srd:report-doc-gap` twice: as
their first step, to drain gaps a prior session left unfiled, and after the
closing line, to offer the gaps this run buffered. When a corpus is reachable,
they also run a facts-vs-corpus pass beside the rule checks: for every
requirement that asserts something about existing system behavior ("the
gateway retries 3×", "the API returns Y"), `search` the corpus to confirm it. A
claim the corpus contradicts is a `reference` finding; one it cannot confirm is
a doc gap for `srd:report-doc-gap`, never a finding in `<srd>.review.md`.
Absent a corpus, skip the pass and review offline. `srd:kb` is not invoked: a
review confirms no platform facts with the user.

## Severity

Tag each finding:

- `blocker` — breaks Quality-Bar acceptance: non-atomic (REQ-1), unverifiable
  (REQ-5/6), uncovered In Scope item (SCO-2; suspended while the In Scope
  `--- TODO ---` marker stands), requirement contradicting Out of Scope
  (SCO-3), undefined term (GLO-3/STR-10), rule hidden in a glossary entry or
  metadata (GLO-1/2), duplicate or out-of-order id (REQ-3/4), missing forward
  link (STR-2/3/5/7), invalid or over-claimed Status (STA-*), an unresolved
  draft scaffold — the In Scope `--- TODO ---` marker or a non-empty `## TODO`
  section (house additions).
- `major` — real defect, does not block: style (LANG-1/2/5/6/7), terminology
  drift, overlapping or duplicate requirements.
- `minor` — cosmetic: British spelling, spacing, punctuation.

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
  contradicting Out of Scope, or a rule stated only in a Note or the
  Introduction (SCO-2, SCO-3).
- `reference` — a link, ticket id, or claim about the live system that is
  wrong or stale.
- `redundancy` — two rules state the same thing, or one subsumes the other.
- `verifiability` — a vague quality, an unmeasurable criterion, an open-ended
  list (REQ-5, REQ-6, LANG-7).
- `atomicity` — one item carrying more than one rule, an example or note
  inside a rule, a rule stating appearance instead of behavior (REQ-1, REQ-7,
  LANG-5, SCO-1).
- `terminology` — one concept under many names, an undefined term, casing that
  drifts from the glossary (GLO-1, GLO-2, GLO-3).
- `linguistic` — grammar, spelling, a missing word, the wrong subject or
  voice, a misplaced or lowercase normative keyword (LANG-1, LANG-2, LANG-3,
  LANG-4, LANG-6).
- `format` — markup, bold identifiers, id numbering, punctuation, spacing
  (REQ-2, REQ-3, REQ-4, REQ-8).

`reference` covers a wrong pointer or fact, `terminology` a diverging word
choice: an SRD that renames an existing platform concept is `terminology`.
Category is orthogonal to `## Errata`: an errata finding is `format` or
`linguistic`, but not every `format` or `linguistic` finding is errata.

## Modes

The review file path is auto-derived, never passed as an argument. `$1` is
the SRD path; `$2` selects the mode (default review when omitted). With no
`$ARGUMENTS`, ask which SRD to review; fall back to the user's prose for
free-form input.

- `$1` only → review (default): read the whole SRD, write the review file.
- `$1` + `walk` → walk: interactive, section by section; record only findings
  the user confirms.
- `$1` + `check` → check: re-verify the review file's open findings against
  the current SRD; tick/move fixed ones, withdraw invalid ones. Trailing
  finding numbers scope it. Hunts no new defects.
- `$1` + `errata` → errata: re-sort an existing review file so errata findings
  sit in `## Errata`. Reclassify only; hunts no new defects.
- `$1` + `feedback` → feedback: emit a terse plain-text issue list of open
  tasks for an email or ticket. No file write.

A file-writing run closes with one task-oriented line — e.g. "4 of 15 tasks
resolved, 2 withdrawn; 1 blocker still open." — plus the per-severity count of
open findings and whether a blocker stands between the SRD and the Quality Bar.
In every mode, report tersely: no preamble or narration; state each fact once;
don't restate output the user can already see.

## Review file format

Every finding carries a global sequential number (`#1..#N`): a plain integer,
permanent, never reused and never renumbered. The next number is `max(all
numbers across open + Resolved + Withdrawn) + 1` — no stored counter; the file
is self-describing.

Each finding is atomic — one indivisible fix, verifiable by a single yes/no. If
two edits can be verified or resolved separately, they are two findings, even
when they share one root cause. No bullet says "do A and B".

Open finding shape — number first, then severity, then category:

`- [ ] #7 [blocker, atomicity] GR-3a: problem — fix. (SRD:REQ-1)`

Close each finding with its rule-id citation namespaced `SRD:` — `(SRD:REQ-1)`,
`(SRD:GLO-3)`. The only rule namespaces are `STR`, `STA`, `LANG`, `REQ`, `GLO`,
and `SCO`; never cite a rule absent from
[../create/references/srd-standard.md](../create/references/srd-standard.md)
(e.g. a defunct `MD-*`). A consistency-pass finding cites `(SRD:consistency)`
and sits under the section where the conflict surfaces; a house-addition
finding (US English, draft scaffolds) cites `(SRD:house)`.

Locate by identifier, never by line number: anchor each finding to the SRD's
own id — requirement (`GR-3a`), scope item (`SC-12`), or glossary term — or,
when no id fits, to the section name verbatim plus a short quote of the
offending text. Never invent shorthand such as `§1.3`; line numbers shift with
formatting. Never quote literal doubled or trailing whitespace as evidence;
describe it in words ("two consecutive spaces before the word *in*"), because
wrapping the review file normalizes whitespace and destroys the quoted proof.

Wrap every finding at 80 columns, breaking onto continuation lines indented two
spaces. Only a single unbreakable token (a long URL or path) may overflow. A
`*(Partial — …)*` note starts its own continuation line.

Layout, in order:

1. `## Errata` first — every open finding that passes the gate and allowlist
   of the errata class in
   [../create/references/errata.md](../create/references/errata.md), grouped
   here instead of under its document section so the author can bulk-apply the
   block via `edit autofix`. The literal heading `## Errata` is the anchor
   `edit autofix` locates; never rename it. Errata findings keep their global
   number, `[minor]` tag, category, and citation. Each states its fix as the
   exact substitution the class requires — literal `` `old` → `new` ``, or for
   whitespace and glyph classes the class plus a neighboring word (`autofix`
   derives the fix) — and a substitution repeated across sites lists every
   site so `autofix` can verify the count. Two different substitutions are two
   findings. Omit the section when empty.
2. Open findings, grouped by document section: Metadata, Introduction,
   Glossary, Scope, Requirements. Omit a section with no open findings. An
   errata finding lives in `## Errata`, never also under its document section.
3. A `---` line, then `## Resolved`: fixed findings as `- [x] #7 …`, a flat
   list sorted by number, keeping the text and rule id.
4. A `---` line, then `## Withdrawn` (last): `- #9 … (withdrawn: <reason>)` —
   no checkbox, keeps the number.

A finding lives in exactly one place. Regression: a resolved finding that
breaks again moves back to its open section, unticked, keeping its number.

Separate consecutive findings with exactly one blank line in every section;
one blank line after a section heading before its first finding.

The metadata is YAML frontmatter with lowercase keys; `prepared` and `updated`
carry a date and time. Include `cfsync-plugin: ignore-push` verbatim so the
Confluence sync never pushes this generated artifact.

```
---
prepared: YYYY-MM-DD HH:MM
updated: YYYY-MM-DD HH:MM
source: path/to/srd.md
cfsync-plugin: ignore-push
---

# SRD Review — <Document Title>

## Errata

- [ ] #8 [minor, linguistic] VIEW-4 uses British spelling: `colour` → `color`.
  (SRD:house)

- [ ] #10 [minor, format] GR-3a: two consecutive spaces after the word "sensor"
  — collapse to one. (SRD:LANG-2)

- [ ] #12 [minor, linguistic] GR-6, GR-9 and DET-2 drop the infinitive:
  `force users re-authenticate` → `force users to re-authenticate`.
  (SRD:LANG-2)

---

## Requirements

- [ ] #3 [blocker, atomicity] GR-3a: states two rules ("validate ... and log
  ...") — split into one rule each. (SRD:REQ-1)

- [ ] #5 [major, redundancy] GR-7 and GR-9 state the same limit in different
  words — merge or remove one. (SRD:consistency)

---

## Resolved

- [x] #1 [blocker, coverage] SC-2 In Scope item had no requirement — added
  GR-11. (SRD:SCO-2)

- [x] #4 [minor, linguistic] British spelling "behaviour" — changed to US.
  (SRD:house)

---

## Withdrawn

- #2 [major, redundancy] GR-5 seemed to overlap GR-6 (withdrawn: distinct
  triggers, confirmed by author).
```

## review (default)

1. Invoke `srd:report-doc-gap` to drain gaps a prior session left unfiled for
   this SRD. Read the entire SRD top to bottom.
2. Check it against every rule in
   [../create/references/srd-standard.md](../create/references/srd-standard.md),
   in document-section order, including the consistency pass and the house
   additions of the authoring guide. When a corpus is reachable, also run the
   facts-vs-corpus pass ([Documentation corpus](#documentation-corpus)),
   handing each doc gap to `srd:report-doc-gap` on discovery.
3. If the review file does not exist, create it and write all findings with
   fresh numbers starting at `#1`, grouped and tagged as above.
4. If it exists, do not rewrite it. First resolve: re-verify open findings and
   tick+move each fixed one to `## Resolved` (a regression moves back, same
   number). Then append newly found defects with fresh numbers — errata to
   `## Errata`, the rest to their document section. Bump `updated:`.
5. Close with the task-oriented line (Modes), then invoke `srd:report-doc-gap`
   to offer the gaps this run buffered.

## walk

Drain `srd:report-doc-gap` as in review, then go section by section in
document order. For each section:

1. Read it and identify every issue, including the facts-vs-corpus pass when a
   corpus is reachable.
2. Present the findings — problem and fix for each. Record nothing yet.
3. Wait for the user to confirm which to keep (all, some, none).
4. Append only confirmed findings to the review file with fresh numbers,
   written as author-facing guidance. Create the file before the first write;
   bump `updated:` on each.
5. Move on only after the user confirms or skips.

After the last section, close as in review step 5.

## check

Re-verify only — hunt no new defects. Keep every number; bump `updated:`.

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
   non-enforceable finding open. No other mode withdraws.
3. Report a short status table: number, current state, assessment.

## errata

Re-sort an existing review file so its errata sit in `## Errata`. Reclassify
only — hunt no new defects. Keep every number; bump `updated:`.

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
2. Leave every other finding untouched; the pass is idempotent.
3. If the review file does not exist, fall through to a normal review.
4. Report which numbers moved ("moved #4, #6, #9 to Errata"); say so when none
   moved.

## feedback

Emit plain text for an email or ticket — no file write:

- Title: `<Document Title> — Review Feedback`.
- Group by section name as a plain heading (no markdown symbols). `## Errata`
  is one such group — list it first, as `Errata`, when it holds open findings.
- One bullet per open finding, blank-line separated. Keep the finding number
  and the SRD's own requirement id (`#7 GR-3a:`), then a one-line
  problem-and-fix. Drop the checkbox, the severity tag, the category tag, and
  the rule-id citation. No bold, no multi-line bullets.
- Open findings only — omit Resolved and Withdrawn.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/srd/review.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
