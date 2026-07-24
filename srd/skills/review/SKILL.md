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

Review an SRD someone else wrote and report what fails the SRD standard. It is
**read-only** — it never edits the source.

## Boundaries

- **Role:** the read-only reviewer of an SRD written by someone else. Produce
  findings; the author acts on them.
- **Owns:** the `<srd>.review.md` file beside the source — its creation,
  structure, numbering, and lifecycle — across **all** modes (`review`, `walk`,
  `check`, `feedback`). No other skill writes it; `edit` never touches it.
- **Must not:** edit the source SRD or fix anything; restate or invent rules —
  defer all format, style, logic, and rules to `create`'s reference files.

## Sources of truth

The rules, checklist, and defect classes live with `create`; this skill
reuses them and never restates a rule. **This skill depends on
`../create/references/*` — do not move or rename `create`. If any
referenced file is missing at run time, stop and tell the user; do not
proceed.** Read these before reviewing:

- [../create/references/srd-standard.md](../create/references/srd-standard.md)
  (eager) — the rules (`STR`, `STA`, `LANG`, `REQ`, `GLO`, `SCO`,
  Quality Bar). The review checks every rule; every finding cites one of
  these ids.
- [../create/references/authoring-guide.md](../create/references/authoring-guide.md)
  (eager) — house extensions (US English, sub-numbering, terminology
  consistency) and the Bad→Good defect classes to recognize; includes the
  consistency pass.

**Apply the full rule set.** `create` leaves STR-2..7 (≥ 2 owners,
Initiative link, Designs link or `N/A` when no UI change) and STA-* (valid
Status; not `ACCEPTED` without an approved design or the Quality Bar) as
placeholders. A finished SRD under review must satisfy them — flag every gap.
Exception: the back-links (STR-4, STR-6) live in the external ticket and design
tool, outside the SRD artifact — the review only checks that the forward
Initiative and Designs links are present in the metadata, and never raises a
back-link finding.

## Documentation corpus (when available)

Some setups expose the platform's live documentation over the `srd-doc` MCP
server — the read tools `mcp__srd-doc__search` (query + optional `k`),
`mcp__srd-doc__get_doc` (document id), and `mcp__srd-doc__list_docs` (no args).
When present, run a **facts-vs-corpus pass** beside the rule checks: for every
requirement that asserts something about existing system behaviour ("the
gateway retries 3×", "the API returns Y"), `search` the corpus to confirm it.
Degrade MCP → the `srd-doc` REST mirror
(`curl 'http://<host>:7777/search?q=TEXT&k=5'`, `.../docs/<id>`) →
scoped Grep/Read over a local corpus checkout, falling through only when a step
genuinely is not there. Absent a corpus, skip the pass and review offline as
before. This stays read-only — it queries the docs, never edits the SRD.

### Reporting a doc gap

When the corpus **cannot confirm** such a claim — missing, wrong, incomplete, or
ambiguous docs — that is a *documentation* gap, not an SRD finding: it never
enters `<srd>.review.md`. Hand it to `srd:report-doc-gap`, which owns capture,
the grill, and the confirmed filing; invoke it on discovery — it buffers the gap
without interrupting the review — and at session start, where it drains any gaps
left unfiled. SRD-standard defects stay in the review file as always; only
corpus deficiencies cross to `report-doc-gap`.

## Severity

Tag each finding:

- **blocker** — breaks Quality-Bar acceptance: non-atomic (REQ-1), unverifiable
  (REQ-5/6), uncovered `In Scope` item (SCO-2 — suspended while the In Scope
  `--- TODO ---` marker stands), requirement contradicting `Out
  of Scope` (SCO-3), undefined term (GLO-3/STR-10), rule hidden in a glossary
  entry or metadata (GLO-1/2), duplicate or out-of-order id (REQ-3/4), missing
  required forward link (STR-2/3/5/7; back-links STR-4/6 are external, never
  flagged), invalid or over-claimed Status (STA-*),
  an unresolved draft scaffold — the In Scope `--- TODO ---` marker or a
  non-empty `## TODO` section (see the authoring guide's house additions).
- **major** — real defect, does not block: style (LANG-1/2/5/6/7), terminology
  drift, overlapping or duplicate requirements.
- **minor** — cosmetic: British spelling, spacing, punctuation.

## Modes

The review file is always `<srd>.review.md` next to the source — auto-derived,
never passed as an argument. `$1` is the SRD path; `$2` selects the mode
(default **review** when omitted). With no `$ARGUMENTS`, ask which SRD to
review; fall back to the user's prose for free-form input.

- `$1` only → **review** (default): read the whole SRD, write the review file.
- `$1` + `walk` → **walk**: interactive, section by section; record only
  findings the user confirms.
- `$1` + `check` → **check**: re-verify the existing review file's open findings
  against the current SRD; tick/move fixed ones, withdraw invalid ones. Does not
  hunt for new defects. Trailing finding numbers (`check #4,6` or `check #4 #6`)
  scope it to those findings only; omitted, it checks every open finding.
- `$1` + `errata` → **errata**: reorganize an existing review file so errata
  findings sit in `## Errata`. Reclassify only; does not hunt for new defects.
- `$1` + `feedback` → **feedback**: emit a terse plain-text issue list of open
  tasks for an email or ticket. No file write.

In every mode, report tersely: no preamble or narration; state each fact once;
don't restate output the user can already see.

## Review file format

Every finding carries a **global sequential number** (`#1..#N`): a plain
integer, permanent, never reused and never renumbered. The next number is
`max(all numbers across open + Resolved + Withdrawn) + 1` — no stored counter;
the file is self-describing. (Plain integers only; `a/b` suffixes belong to the
SRD's own ids like `GR-3a`, never to findings.)

Each finding is **atomic** — one indivisible fix, verifiable by a single
yes/no. The boundary is **independent verifiability**: if two edits can be
verified or resolved separately, they are two findings, even when they share
one root cause. No bullet says "do A and B".

Open finding shape — number first, then severity:

`- [ ] #7 [blocker] GR-3a: problem — fix. (SRD:REQ-1)`

Close each finding with its rule-id citation **namespaced `SRD:`** — e.g.
`(SRD:REQ-1)`, `(SRD:GLO-3)` — marking it an SRD-standard rule. The only rule
namespaces are `STR`, `STA`, `LANG`, `REQ`, `GLO`, and `SCO`; never cite a rule
absent from
[../create/references/srd-standard.md](../create/references/srd-standard.md)
(e.g. a defunct `MD-*`). A consistency-pass finding cites `(SRD:consistency)`.

**Locate by identifier, never by line number.** Anchor each finding to the
SRD's own id — requirement (`GR-3a`), scope item (`SC-12`), or glossary term —
or, when no id fits, to the section name **verbatim** plus a short quote of the
offending text. Use only ids and headings that actually appear in the SRD; never
invent section shorthand such as `§1.3` — the SRD does not use `§`. Line numbers
shift with formatting and are unreliable; never cite them.

Break a long finding onto continuation lines indented two spaces (aligning
under the bullet text). Line length is not constrained.

Layout, in order:

1. `## Errata` **first**, at the very top of the open findings — every open
   finding whose fix is *mechanical and meaning-preserving* per the errata class
   in the authoring guide (spelling, punctuation, stray/wrong emphasis, spacing;
   **not** line-wrapping, and **not** any ambiguous case — classify
   conservatively). Grouped here instead of under its document section, so the
   author can bulk-apply the block via `edit autofix`. The literal heading
   `## Errata` is the machine anchor `edit autofix` locates; do not rename it.
   Errata findings keep their global number, their `[minor]` tag, and their
   citation, exactly like any other finding. Omit the section when empty.
2. **Open findings**, grouped by document section: Metadata, Introduction,
   Glossary, Scope, Requirements. Omit a section with no open findings. An errata
   finding lives in `## Errata`, never also under its document section.
3. A `---` line, then `## Resolved`: fixed findings as `- [x] #7 …`, a flat
   list **sorted by number** (section grouping dropped), keeping the text and
   rule id.
4. A `---` line, then `## Withdrawn` (last): `- #9 … (withdrawn: <reason>)` —
   **no checkbox**, keeps the number.

A finding lives in exactly one place. **Regression:** a resolved finding that
breaks again moves back to its open section, unticked, keeping its original
number — the same defect keeps its history.

Separate consecutive findings with **exactly one blank line** — in every
section — so a long list reads as distinct blocks, not a wall of text. One
blank line after a section heading before its first finding; never two.

The metadata is YAML frontmatter with lowercase keys; `prepared` and `updated`
carry a date **and time**. Include `cfsync-plugin: ignore-push` verbatim so the
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

- [ ] #8 [minor] VIEW-4 uses British "colour" — change to US "color".
  (SRD:LANG-1)

- [ ] #10 [minor] GR-3a: doubled space after "sensor" — collapse to one.
  (SRD:LANG-7)

---

## Requirements

- [ ] #3 [blocker] GR-3a: states two rules ("validate ... and log ...") — split
  into one rule each. (SRD:REQ-1)

- [ ] #5 [major] GR-7 and GR-9 state the same limit in different words — merge
  or remove one. (SRD:consistency)

---

## Resolved

- [x] #1 [blocker] SC-2 In Scope item had no requirement — added GR-11.
  (SRD:SCO-2)

- [x] #4 [minor] British spelling "behaviour" — changed to US. (SRD:LANG-1)

---

## Withdrawn

- #2 [major] GR-5 seemed to overlap GR-6 (withdrawn: distinct triggers,
  confirmed by author).
```

## review (default)

1. Read the entire SRD top to bottom.
2. Check it against every rule in
   [../create/references/srd-standard.md](../create/references/srd-standard.md),
   in document-section order, including the consistency pass and the house
   additions. When a corpus is available, also run the facts-vs-corpus pass
   (see [Documentation corpus](#documentation-corpus-when-available)) and
   delegate any doc gap to `srd:report-doc-gap`, keeping it out of the review
   file.
3. If the review file does not exist, create it and write all findings with
   fresh numbers starting at `#1`, grouped and tagged as above — every errata
   finding under `## Errata`, the rest under their document section.
4. If it already exists, do not rewrite it. First **resolve**: re-verify open
   findings and tick+move each fixed one to `## Resolved` (a regression moves
   back to its open section, same number). Then **append** newly found defects
   with fresh numbers — errata to `## Errata`, the rest to their document
   section. Bump the `updated:` frontmatter.
5. Close with the task-oriented summary (see Closing).

## walk

Go section by section in document order. For each section:

1. Read it and identify every issue.
2. Present the findings — problem and fix for each. Record nothing yet.
3. Wait for the user to confirm which to keep (all, some, none).
4. Append only confirmed findings to the review file with fresh numbers,
   written as author-facing guidance. Create the file before the first write;
   bump the `updated:` frontmatter on each.
5. Move on only after the user confirms or skips. Never edit the source.

## check

Given the current SRD and its existing review file, **re-verify only** — do not
hunt for new defects. Keep every number; bump the `updated:` frontmatter.

Trailing finding numbers **scope the pass** to just those findings; the rest
stay untouched. Accept them comma- or space-separated, `#` optional —
`check #4,6`, `check #4 #6`, `check 4,6` all name findings #4 and #6. Report any
listed number that is absent or already resolved/withdrawn, and check the rest.
Omitted, check every open finding.

1. For each finding in scope, judge it against the current text and map its
   state:
   - **fixed** → tick `[x]` and move to `## Resolved`.
   - **partial** → stays `[ ]` in its section with `*(Partial — …)*` appended.
     Never ticks.
   - **not addressed** → stays `[ ]`, untouched.
2. **Withdrawal is check-only:** if a finding proves invalid (mistaken, the
   author justified the text, or it cites a rule absent from the standard such
   as a defunct `MD-*`), move it to `## Withdrawn` with a reason. Never carry a
   non-enforceable finding open. No other mode withdraws.
3. Report a short status table: number, current state, assessment.

## errata

Reorganize an **existing** review file so its errata sit in `## Errata` — a
one-time retrofit for files written before the block existed, and a re-sort on
demand. **Reclassify only — never hunt for new defects** (like `check`). Keep
every number; bump the `updated:` frontmatter.

1. For each open finding, test it against the errata class in
   [../create/references/authoring-guide.md](../create/references/authoring-guide.md).
   If it qualifies and is not already under `## Errata`, move it there —
   **keeping its number**, `[minor]` tag, and citation; create the `## Errata`
   section at the top if absent. Classify conservatively: leave ambiguous
   findings where they are.
2. Leave every non-errata finding, and every already-placed errata finding,
   untouched. The pass is **idempotent** — a second run changes nothing.
3. If the review file does not exist, fall through to a normal **review**.
4. Report which numbers moved (e.g. "moved #4, #6, #9 to Errata"); say so when
   none moved.

## feedback

Emit plain text for an email or ticket — no file write:

- Title: `<Document Title> — Review Feedback`.
- Group by section name as a plain heading (no markdown symbols). `## Errata`
  is one such group — list it first, as `Errata`, when it holds open findings.
- One bullet per **open** finding, **blank-line separated** (as in the review
  file). Keep the finding number and the SRD's own requirement id (e.g.
  `#7 GR-3a:`), then a one-line problem-and-fix. Drop the checkbox, the severity
  tag, and the standard rule-id citation. No bold, no multi-line bullets.
- List open findings only — omit Resolved and Withdrawn.

## Closing

Close a file-writing run with one **task-oriented** line — e.g. "4 of 15 tasks
resolved, 2 withdrawn; 1 blocker still open." — alongside the per-severity
count of open findings and whether any blocker stands between the SRD and the
Quality Bar.

## Consistency pass

Run the consistency pass in
[../create/references/authoring-guide.md](../create/references/authoring-guide.md).
Report each consistency finding under the section where the conflict surfaces,
citing the rule id as `(SRD:<id>)`, or `(SRD:consistency)`.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/srd/review.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
