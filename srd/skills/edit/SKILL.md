---
name: edit
description: >
  Improves an existing Software Requirement Document (SRD) by editing it in
  place against the SRD standard. Use when asked to edit, improve, fix,
  revise, or clean up an SRD, or to apply findings from a review file or
  pasted feedback.
argument-hint: "<path to SRD> [<review-file> | #n | <line> | autofix | polish | <target>]"
license: MIT
---

# edit

## Usage

```
/edit <srd>                  interactive (default): front-load issues, then walk entry by entry
/edit <srd> 123              interactive from line 123: resolve to the nearest entry, walk from there
/edit <srd> <srd>.review.md  feedback: apply a review file or pasted feedback, Scope last, blocker → major → minor
/edit <srd> #2               feedback from finding #2, then next by number or jump to any number
/edit <srd> autofix          bulk-apply the review's ## Errata block behind one confirmation
/edit <srd> polish           mechanical-only cleanup (spelling, numbering, keywords), confirm each
/edit <srd> GR-3a            targeted: edit one entry by id, quoted text, or description
```

Drive an existing SRD toward the SRD standard by editing the source in place.

## Boundaries

The write-only editor of an existing SRD, one confirmed edit at a time — the
counterpart to the read-only `review`. It never invents or restates rules
(format, style, logic, and rules come from `create`'s reference files) and
never edits metadata (Owners, Initiative, Designs), sets back-links, or changes
`Status`; it flags those gaps (STR-2/3/5/7, STA-*). A finding outside that
mandate is reported as the author's to fix, not looped — even when the run
entered at it: a feedback run starting at a metadata `#2` says so and advances
to `#3`. An explicit `#n`
sets the order for the rest of the run: walk ascending from `n` to the end,
then come back for the lowest still open; a jump re-anchors the walk the same
way. It never proposes a Status
transition (flag only a malformed `STA-*` value) and never proposes pushing,
publishing, or syncing the SRD as a follow-up. Comment blocks are read-only:
a source of information about the SRD, never edited, answered, or rewritten,
even when they hold stale references. Back-links (STR-4/6) are
external: check that the forward Initiative and Designs links are present and
never flag a back-link gap. Acceptance is a human decision. It maintains the
two [draft scaffolds](#draft-scaffolds) and resolves them only on the user's
signal. It never writes `<srd>.review.md` — `review` owns that file; `edit`
reads it and hands off to `review <srd> check` to update it. It owns
`<srd>.decisions.md` (see [Decision log](#decision-log)); no other skill writes
that file.

## Sources of truth

The rules, checklist, procedures, template, and glossary live with `create`;
reuse them, never duplicate. **This skill depends on `../create/references/*`
and `../create/assets/*` — do not move or rename `create`. If a referenced file
is missing at run time, stop and tell the user.**

- [../create/references/project-config.md](../create/references/project-config.md)
  (eager) — the gate, and the project paths, standard, and server it names.
- The SRD standard (eager, fetched live per that file) — the rules (`STR`,
  `STA`, `LANG`, `REQ`, `GLO`, `SCO`, Quality Bar); every edit and check cites
  these ids.
- [../create/references/authoring-guide.md](../create/references/authoring-guide.md)
  (eager) — house extensions (US English, sub-numbering, one term per concept,
  the consistency pass) and the Bad→Good defect classes to fix toward.
- [../create/references/doc-corpus.md](../create/references/doc-corpus.md) and
  [references/corpus-edits.md](references/corpus-edits.md) (on-demand: the
  first edit that asserts something about existing system behavior or removes
  a requirement) — how to
  reach the corpus and where an unconfirmed fact goes, and when this skill
  looks, what it states in the proposal, and what the confirmation attests.
- [../review/references/review-file.md](../review/references/review-file.md)
  (on-demand: feedback, autofix) — how `<srd>.review.md` is numbered, cited and
  laid out. Never infer the shape.
- [../create/references/errata.md](../create/references/errata.md) (on-demand:
  autofix) — the gate, allowlist, and exclusions of the bulk-fix errata class.
- [../create/references/srd-procedures.md](../create/references/srd-procedures.md)
  (on-demand: the first proposal that touches a term, for glossary resolution;
  Generate In Scope for the derivation procedure).
- [../create/assets/srd-template.md](../create/assets/srd-template.md)
  (on-demand: restructuring) — the required section order.

## Documentation corpus

Procedure, trust, and where an outcome goes:
[../create/references/doc-corpus.md](../create/references/doc-corpus.md). When
*this skill* consults it — the lookup before the proposal, the
set-versus-reported reading, what a confirmation attests, where a deferred
platform question goes — is in
[references/corpus-edits.md](references/corpus-edits.md).

## Session start (every mode)

Spend nothing this run does not need before the user's first question or
proposal. Run the project gate first
([../create/references/project-config.md](../create/references/project-config.md)),
then resolve the mode ([Modes](#modes)): one that cannot run — `#n` or
`autofix` with no `<srd>.review.md` — says so and stops before step 1: a run
that will do nothing has nothing to read or check.
Otherwise three steps, no questions of its own.

1. Read the whole SRD top to bottom — every mode, however narrow the target: a
   cross-reference in an unread section is the one the edit breaks.
2. Run the draft check in
   [../create/references/doc-corpus.md](../create/references/doc-corpus.md);
   say nothing about an empty result as it happens — the manifest carries it.
3. Approval gate: read `Status` — `ACCEPTED` is approved, anything else
   in-progress — state which in one clause and go; it is the reply's only
   setup line (no gate, standard, draft-check or glossary report). Never ask
   the user to confirm it: every id change the gate governs is confirmed again
   in the loop.

`autofix` runs only steps 1–2: errata never touches ids or terms.

### Glossary (on the first term)

Nothing about the glossary happens at session start: a run that reaches no term
never calls `glossary_terms`. The procedure in
[../create/references/srd-procedures.md](../create/references/srd-procedures.md)
waits for the first thing that needs a term settled and lands before it: the
first proposal that introduces, renames or rests on a possibly company-defined
term, or in `interactive` the step-1 summary, which promises every issue found
and so owes GLO-3 too. A term put to the user against an unloaded term set is a
GLO-3 miss. Hold the set for the session; `polish` and `autofix` never reach it.
This skill asks no setup question.

## Id rules

Two invariants hold without reading anything: on an approved SRD ids are frozen
and content changes need STA-4, and any id change is stated and approved in the
loop's confirmation, never applied quietly. The rest — sub-numbering, removal
under STA-8, renumbering, comment blocks — is in
[references/id-rules.md](references/id-rules.md), read before the first
proposal on an approved SRD or any proposal touching an id.

## Edit discipline

When listing the issues found before the loop, keep only findings that survive
scrutiny — a real rule violation, not a preference. Requirements that read as
overlapping are often independently testable (a disabled control vs a grayed
one; a length cap vs its truncation format); a scope item covering one
capability across many surfaces is atomic; a compound term whose parts are in
the Company Glossary needs no entry. A finding withdrawn mid-session costs the
user's trust in the whole list.

Every mode but `autofix` runs this loop per change:

1. Propose exactly one change: its location, the problem (cite the rule id),
   the before and after text, and a one-line rationale. Never invent a figure
   neither the SRD nor the user gives: the after text holds a placeholder
   (`<lockout minutes>`). A change asserting
   existing system behavior gets its corpus lookup here, before the proposal is
   put, and the proposal states what it found — a KB section it contradicts
   included, as a finding no `rank` settles
   ([references/corpus-edits.md](references/corpus-edits.md)). A removal gets
   one too: each KB section only the cut requirement asserted for this SRD gets
   a `wrong` gap on the cut's confirmation. Name the
   location the way the user can find it in the file — the requirement, scope,
   or glossary id, and for prose that has none the line number. Never an
   ordinal the user would have to count out ("paragraph three"); this holds for
   what comes next as much as for the proposal itself.
2. Close the proposal with the choices (Yes / Yes Next / Skip / Edit) — the
   capital letter is the key — and apply only on explicit approval:
   - `Y` (Yes): apply, then stay on the current entry and propose its next
     issue; when that entry has no more, say so and name the way on ("nothing
     further on GR-3 — next entry, or name one"), then stop. `Y` never advances
     the walk, and the user should not have to guess what does. In
     `feedback` the unit is the review's finding, not the entry, so `Y`
     proposes the next finding on that entry and stops when the review has no
     more — never an issue the review did not raise. Applying a review means
     applying that review.
   - `YN` (Yes Next): apply and move to the next entry, leaving its remaining
     issues flagged.
   - `S` (Skip): change nothing; leave the issue flagged. Like `Y`, it does not
     advance the walk, even when it was the entry's last issue.
   - `E` (Edit): apply the user's amended text in place of the proposal.
   Advance to the next entry only on `YN` or an explicit ask — never on `Y`,
   `E` or `S`, however little the entry has left; once an entry is resolved,
   stop and wait, never walking ahead even for a read-only look. Never batch
   unrelated changes; never edit without confirmation. Ask one question at a
   time — the confirmation *is* that question. Never widen it into a menu of
   variants (`E1`/`E2`), never pair it with an open design question or an offer
   to do something else, and never put the held-over questions to the user as a
   set. When a proposal has two defensible wordings, pick one and propose it;
   `E` is how the user takes the other. Anything held over goes in an `## Open
   questions` numbered list — one line each, no rationale — that you carry
   silently and draw from one item at a time, in the order the user set. That
   list is terminal output, not a section of the SRD: it belongs to this
   session and empties with it. Show it only
   when the user asks what is still open, renumbered from 1 each time so
   answered items leave no holes; what remains at the end goes in the closing
   manifest.
3. Re-validate what the applied edit touched, against the standard: scope
   coverage (SCO-2/3, suspended while the In Scope `--- TODO ---` marker
   stands), id uniqueness/order (REQ-3/4), term use (GLO-3), and anything
   referencing or referenced by the edit. Report a problem the fix introduced.
   No corpus lookup happens here: step 1 already did it
   ([references/corpus-edits.md](references/corpus-edits.md)).
4. Log the change in `<srd>.decisions.md` before proposing the next one (see
   [Decision log](#decision-log)).

Write every edit to the LANG and REQ rules and the authoring guide (US English,
one term per concept); a restructuring edit follows the template's order.

## Decision log

Every applied edit is recorded in `<srd>.decisions.md` beside the source.
What goes in an entry, the file's shape, and what `autofix` owes it are in
[references/decision-log.md](references/decision-log.md) — read it before
writing the session's first entry.

## Draft scaffolds

Two working scaffolds live in a draft SRD (House additions in the authoring
guide). Maintain them across every mode and never remove either silently; both
block `ACCEPTED` and are reported as follow-ups at session end.

- In Scope `--- TODO ---` marker: while `### In Scope` holds only this marker,
  In Scope is knowingly pending — suppress every SCO-2 / In-Scope-coverage
  complaint (issue summary, re-validation, consistency pass) and do not
  fabricate `SC-n` items.
- `## TODO` section: a numbered list of open issues the human must return to,
  kept as the document's last section.

On "Add X to TODO", or on the user's signal that the requirements are complete
(or an ask to fill In Scope), follow
[references/draft-scaffolds.md](references/draft-scaffolds.md), which carries
both procedures and what each may touch. Never trigger the In Scope derivation
on your own.

## Modes

The first token is the SRD path; the next selects the mode, interactive when
omitted. With no arguments, ask which SRD to edit.

Prose after the path is feedback when it is a list of findings, targeted when
it names one entry and what to do to it ("fix the vague 'fast' requirement").
A single pasted finding is both: take it as targeted, which walks one entry
with a confirmation and expects no review file.

- the SRD path only → interactive.
- path + a bare integer → interactive from that line.
- path + a `.review.md` path, or pasted feedback → feedback.
- path + `#n` → feedback from finding `#n`.
- path + `autofix` → autofix.
- path + `polish` → polish.
- path + anything else (id, quoted text, description) → targeted.

### interactive (default)

1. Front-load a grouped issue summary — every issue found, grouped by document
   section (Metadata, Introduction, Glossary, Scope, Requirements), each citing
   its rule id. Edit nothing yet; the first proposal may follow in the same
   turn.
2. Walk entry by entry in document order — each requirement (`PFX-n`), glossary
   term, scope item — running the loop for every fix the user approves; Scope
   goes last, after Requirements, since it derives from them.
   Move on only on `YN` or an explicit ask, and never before the current entry
   is resolved or skipped. An entry with no finding resolves on sight: say so
   and move on — nothing was proposed, so no key is owed.

Start point (path + line): resolve the line to the entry or paragraph at or
nearest it, skip step 1, and begin step 2 there, continuing to the end; Scope
entries at or after the start still go last, those before it are skipped. The
walk is still one entry at a time and still never looks ahead — step 1's
summary is what would have told you which later entry has a finding, and
skipping it means learning that entry by entry, never by scanning forward.

### feedback

Apply findings from a review; the review file stays untouched regardless of
outcome.

1. Input is a `<srd>.review.md` path or feedback pasted inline (email, ticket,
   chat); parse the findings from either.
2. Work findings in two passes: every section but Scope, then Scope, which
   derives from the settled requirements (SCO-2/3).
   Within each pass, severity order — blocker → major → minor — using the
   review's tags and numbers; judge untagged pasted feedback from the rule.
3. Run the loop per finding; reference findings by number in the closing
   manifest.
4. Close by pointing the user to `review <srd> check` to reclassify what
   landed.

Start point (path + `#n`): requires an existing `<srd>.review.md` (the SRD's
path with `.md` replaced: `specs/login.md` → `specs/login.review.md`); if
absent, say so and stop — one or two lines naming the missing file, nothing
more. No approval-gate line, draft check, manifest, or way in — not even "run
`srd:review` first": those report a run that happened, and this one did not.
Enter at finding `#n` instead of the passes and severity order; after each
finding, default to the next by number or jump to any number the user names.

### autofix

Bulk-apply the `## Errata` block of `<srd>.review.md` behind one batch
confirmation — never the edit loop, never a re-scan of the SRD. The full
procedure is in [references/autofix.md](references/autofix.md) *(on-demand:
this mode only)*: read it before applying anything.

### polish

Mechanical-only cleanup through the loop, confirming each change, in document
order with no summary first; metadata gaps go to the closing manifest, not the
walk. Scope:
British → US spelling, identifier format/order (REQ-2/3/4, subject to the
approval gate), keyword capitalization (LANG-4), valid Markdown, requirement-group
dividers (authoring guide), stray example/note text (REQ-7), spacing and punctuation. Never rewrite requirement
meaning, restructure, or cut a requirement.

### targeted

Edit one entry the user points to by requirement id (`GR-3a`), quoted text, or
free description ("the login timeout rule").

1. Locate the target; for quoted text or a description, confirm the match
   before editing, inside the proposal: it is the loop's one question, so say
   the match outright ("taking 'fast' to be GR-4"), and `E` corrects it. With
   nothing to fix on it, say so and ask what they want changed rather than
   manufacturing a finding.
2. Run the loop on that entry; its resolution ends the run (Session end).
3. Report the re-validation result explicitly: whether the edit introduced any
   inconsistency in the entry or its cross-refs.

## Session end (every mode)

1. Re-check the whole document against every rule in the standard plus the
   consistency pass in the authoring guide, and report what remains. GLO-3
   covers only terms this session already settled: a session that never loaded
   the term set does not load it here.
2. Invoke `srd:report-doc-gap` to offer the draft gaps this session captured,
   only when there are any. The start check covers what a *prior* session
   left; this covers what *this* session produced. `srd:kb` already wrote each
   attested fact, and every cut's `wrong` gaps were filed, at its
   confirmation.
3. Close with the manifest — approved edits, not a re-narration of diffs the
   user already saw:
   - What changed: entry/id, one line each; a cut carries the ids of the
     `wrong` gaps it filed.
   - What was flagged and left (frozen-id conflicts, metadata gaps, anything
     the user declined).
   - Outstanding human follow-ups: placeholders, Status, and either draft
     scaffold left standing — by name and item count, not its items.
   - `## Open questions`: what remains of the held-over list, numbered from 1,
     one line each — the list itself, never a bare count.
   - `Decision log: <srd>.decisions.md — hand the author its newest block,
     ## <date>, as this session's summary`, with the block's real heading;
     omitted when nothing was applied, since the file does not exist.
   - One start clause: what the draft check found, which delegates ran,
     whether the glossary resolved — a check that found nothing otherwise looks
     like one that never ran.

`autofix`'s exceptions are listed here and nowhere else: it skips step 1
(surface-only fixes) and invokes no delegate in step 2 (it attests no fact and
captures no gap; a prior session's drafts were checked at session start). It
owes step 3's manifest like every mode, plus what
[references/autofix.md](references/autofix.md) step 8 adds.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. Every count in the manifest — requirements
checked, edits applied, findings open, questions carried — is read off the
finished file, never carried from the work.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/srd/edit.md`, the
sibling winning a conflict — a read-only install writes the second, and what it
learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule to the sibling when this directory
is writable, else to the fallback, creating it, and report where.