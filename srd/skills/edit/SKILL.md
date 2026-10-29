---
name: edit
description: >
  Improves an existing Software Requirement Document (SRD) by editing it in
  place against the SRD standard. Use when asked to edit, improve, fix,
  revise, or clean up an SRD, to open one for editing, or to apply findings
  from a review file or pasted feedback.
argument-hint: "<path to SRD> [walk | <line> | <id> | <review-file> | #n | autofix | polish | summary | <target>]"
license: MIT
---

# edit

## Usage

```
/srd:edit <srd>                  load (default): read the SRD, its decision log and review, then wait for edit prompts
/srd:edit <srd> walk             interactive: front-load issues, then walk entry by entry
/srd:edit <srd> 123              interactive from line 123: resolve to the nearest entry, walk from there
/srd:edit <srd> ABC-5            interactive from ABC-5: walk from that requirement or scope entry
/srd:edit <srd> <srd>.review.md  feedback: apply a review file or pasted feedback, scope last, blocker → major → minor
/srd:edit <srd> #2               feedback from finding #2, then next by number or jump to any number
/srd:edit <srd> autofix          bulk-apply the review's ## Errata block behind one confirmation
/srd:edit <srd> polish           mechanical-only cleanup (spelling, numbering, keywords), confirm each
/srd:edit <srd> summary [today]  read-only: newest decision-log block (or a day; `<date> <HH:MM>` one block) as a chat message
/srd:edit <srd> ABC-3a <change>  targeted: edit one entry by id plus the change, quoted text, or description
```

Drive an existing SRD toward the SRD standard by editing the source in place.

## Boundaries

The write-only editor of an existing SRD, one confirmed edit at a time — the
counterpart to the read-only `review`. It never invents or restates rules
(format, style, logic, and rules come from the standard and `create`'s
reference files) and never edits the header fields the standard defines, sets
back-links, or changes the status field; it flags those gaps under the rules
that govern them. A finding outside that mandate is reported as the author's
to fix, not looped — even when the run entered at it
([references/modes.md](references/modes.md)). It never proposes a status
transition (flag only a value outside those the standard lists) and never
proposes pushing, publishing, or syncing the SRD as a follow-up. Comment blocks
are read-only: a source of information about the SRD, never edited, answered,
or rewritten, even when they hold stale references, unless the user explicitly
asks to resolve one. Back-links the standard requires of linked documents are
external: check that the SRD's own forward links are present and never flag a
back-link gap. Acceptance is a human decision. It never writes
`<srd>.review.md` — `review` owns that file; `edit` reads it and hands off to
`review <srd> check` to update it. It owns `<srd>.decisions.md` (see
[Decision log](#decision-log)).

## Sources of truth

The rules, checklist, procedures, template, and glossary live with `create`;
reuse them, never duplicate. **This skill depends on `../create/references/*`
and `../create/assets/*` — do not move or rename `create`. If a referenced file
is missing at run time, stop and tell the user.**

- [../create/references/project-config.md](../create/references/project-config.md)
  (eager) — the gate, and the project paths, standard, and server it names.
- The SRD standard (eager, fetched live per that file) — the only source of
  rules: sections and their order, header fields, status values, identifier
  format, wording, terms, scope, and any acceptance checklist. Act only on what
  it states; every edit and check cites the identifier of the rule it rests
  on, as the standard writes it.
- [../create/references/authoring-guide.md](../create/references/authoring-guide.md)
  (eager) — house extensions (US English, sub-numbering, one term per concept,
  the consistency pass) and the Bad→Good defect classes to fix toward.
- [../create/references/doc-corpus.md](../create/references/doc-corpus.md) and
  [references/corpus-edits.md](references/corpus-edits.md) (on-demand: the
  first edit that changes a requirement's meaning or removes one) — how to
  reach the corpus and where an unconfirmed fact goes, and how this skill
  uses it.
- [../review/references/review-file.md](../review/references/review-file.md)
  (on-demand: feedback, autofix) — how `<srd>.review.md` is numbered, cited and
  laid out. Never infer the shape.
- [../create/references/errata.md](../create/references/errata.md) (on-demand:
  autofix) — the gate, allowlist, and exclusions of the bulk-fix errata class.
- [../create/references/srd-procedures.md](../create/references/srd-procedures.md)
  (on-demand: the first proposal that touches a term, for glossary resolution;
  its in-scope derivation procedure).
- [../create/assets/srd-template.md](../create/assets/srd-template.md)
  (on-demand: restructuring) — the house layout; the section order is the
  standard's.

## Session start (every mode)

Spend nothing this run does not need before the user's first question or
proposal. Run the project gate first
([../create/references/project-config.md](../create/references/project-config.md)),
then resolve the mode ([Modes](#modes)): one that cannot run — `#n` or
`autofix` with no `<srd>.review.md` — says so and stops before step 1: a run
that will do nothing has nothing to read or check. `load` runs the gate and
its own reads ([load](references/modes.md#load-default)), nothing below.
Otherwise three steps, no questions of its own.

1. Read the whole SRD top to bottom — every mode, however narrow the target: a
   cross-reference in an unread section is the one the edit breaks.
2. Run the draft check in
   [../create/references/doc-corpus.md](../create/references/doc-corpus.md);
   say nothing about an empty result as it happens — the manifest carries it.
3. Approval gate: read the status field against the standard's lifecycle
   rules — *frozen* when they forbid renumbering at that value, *under
   sign-off* when a change in meaning needs sign-off there, both when both
   hold (apply both rule sets), else in-progress — state which in one clause
   and go; it is the reply's only setup line (no
   gate, standard, draft-check or glossary report). Never ask
   the user to confirm it: every id change the gate governs is confirmed again
   in the loop.

`autofix` runs only steps 1–2: errata never touches ids or term wording.
`summary` runs only step 1.

### Glossary (on the first term)

Nothing about the glossary happens at session start, and this skill asks no
setup question. When the term set loads is in
[references/proposals.md](references/proposals.md#glossary); `polish` and
`autofix` reach it only for a first-use link the standard requires.

## Id rules

Two invariants hold without reading anything: on a frozen SRD ids are frozen,
and under sign-off content changes need the sign-off the standard sets; any id
change is stated and approved in the loop's confirmation, never applied
quietly. The rest — sub-numbering, removed requirements, renumbering, comment
blocks — is in [references/id-rules.md](references/id-rules.md), read before
the first proposal on a frozen or under-sign-off SRD or any touching an id.

## Edit discipline

Every mode but `autofix` runs this loop per change:

1. Propose exactly one change: its location, the problem (cite the rule id), the
   before text quoted verbatim from the file, the after text built from that
   quote, and a one-line rationale. Never invent a figure
   neither the SRD nor the user gives: the after text holds a placeholder
   (`[TBD: lockout minutes]` — never `<…>`, which Markdown renderers read as an
   HTML tag). Fix only what the finding names, with the smallest wording change
   that settles it; never add a fact, condition, permission, or platform detail
   the SRD lacks unless the user asks. A change to a requirement's meaning — one
   the user dictates mid-walk included — or a removal gets its corpus lookup
   here, before the proposal is put
   ([references/corpus-edits.md](references/corpus-edits.md)).
2. Close the proposal with the choices (Yes / Yes Next / Skip / Edit) — the
   capital letter is the key — and apply only on explicit approval. If the
   file changed on disk since the approval gate, re-read the status field
   first: a value now under sign-off puts the edit under that rule, asked
   before it lands. What
   counts as a finding, how a fix is worded, what each key does, and where
   held-over questions go are in
   [references/proposals.md](references/proposals.md), read before the
   interactive summary or the first proposal. Advance to the next entry only
   on `YN` or an explicit ask — never on `Y`, `E` or `S`, however little the
   entry has left; once an entry is resolved, stop and wait, never walking
   ahead even for a read-only look. Never batch unrelated changes; never edit
   without confirmation.
3. Re-validate what the applied edit touched, against the standard's rules
   on scope coverage (suspended while the in-scope `--- TODO ---` marker
   stands), identifier uniqueness and order, and term definition, and anything
   referencing or referenced by the edit. Report a problem the fix introduced.
4. Log the change in `<srd>.decisions.md` before proposing the next one (see
   [Decision log](#decision-log)).

Two fixes skip the loop in every mode (`autofix` takes them only as errata) —
a first-use link the standard requires and a heading off its siblings' title
case: apply, log,
report in one line, and go on — never ask. What each covers and what goes
through the loop instead:
[references/proposals.md](references/proposals.md#fixes-that-skip-the-loop)
(on-demand: the first such fix).

Write every edit to the standard's wording and requirement rules and the
authoring guide (US English, one term per concept); a restructuring edit
follows the standard's section order.

## Decision log

Every applied edit is recorded in `<srd>.decisions.md` beside the source.
What goes in an entry, the file's shape, and what `autofix` owes it are in
[references/decision-log.md](references/decision-log.md) — read it before
writing the session's first entry.

## Draft scaffolds

A draft SRD may hold two working scaffolds: the in-scope `--- TODO ---` marker
and a `## TODO` section. Maintain them across every mode and never remove either
silently; both block approval and are reported as follow-ups at session end.
When the SRD holds either, on "Add X to TODO", or on the signal to fill the
in-scope list, read
[references/draft-scaffolds.md](references/draft-scaffolds.md) (on-demand) —
what each scaffold suppresses, and both procedures. Never trigger
the in-scope derivation on your own.

## Modes

The SRD path comes first; a mode word may sit anywhere after it, the rest keep
their documented order, and no mode means load. With no arguments, ask which
SRD to edit.

Prose after the path is feedback when it is a list of findings, targeted when
it names one entry and what to do to it ("fix the vague 'fast' requirement").
A single pasted finding is both: take it as targeted, which walks one entry
with a confirmation and expects no review file.

- the SRD path only → load.
- path + `walk` → interactive.
- path + a bare integer → interactive from that line.
- path + a bare requirement or scope id, no change named → interactive from
  that entry: a walk to the end, not a one-entry edit.
- path + a `.review.md` path, or pasted feedback → feedback.
- path + `#n` → feedback from finding `#n`.
- path + `autofix` → autofix.
- path + `polish` → polish.
- path + `summary`, optionally `today`, a date, or a date and time → summary.
- path + anything else (an id plus a change, a glossary term, quoted
  text, description) → targeted.

A `key=value` that names no control here, or a word left over once the modes,
the target, and any text the skill takes are read: say it was not recognized,
name the ones that exist, and run with the defaults as if it were absent —
unless dropping it would widen what the run changes; then ask. A target that
resolves to nothing: say so and ask — never guess what to work on.

### Mode procedures

Read the mode's procedure before it does anything *(on-demand: that mode
only)*:

- load (default): open the SRD for the user's own edit prompts; find and
  propose nothing —
  [references/modes.md](references/modes.md#load-default).
- interactive (`walk`): a grouped issue summary, then the loop entry by entry
  in document order, scope last — [references/modes.md](references/modes.md).
- feedback, polish, targeted: findings from a review or pasted feedback,
  mechanical-only cleanup, or one entry the user points to with the change
  wanted — [references/modes.md](references/modes.md).
- autofix: bulk-apply the `## Errata` block of `<srd>.review.md` behind one
  batch confirmation — never the edit loop, never a re-scan of the SRD —
  [references/autofix.md](references/autofix.md).
- summary: read-only, writing no file —
  [references/summary.md](references/summary.md).

## Session end (every mode)

1. Re-check the whole document against every rule in the standard plus the
   consistency pass in the authoring guide, and report what remains. The
   term-definition rule covers only terms this session already settled: a
   session that never loaded the term set does not load it here.
2. Invoke `srd:report-doc-gap` to offer the draft gaps this session captured,
   only when there are any
   ([references/corpus-edits.md](references/corpus-edits.md#session-end)).
3. Close with the manifest — approved edits, not a re-narration of diffs the
   user already saw:
   - What changed: entry/id, one line each; a cut carries its `wrong` gap ids
     ([references/corpus-edits.md](references/corpus-edits.md)).
   - What was flagged and left (frozen-id conflicts, metadata gaps, anything
     the user declined).
   - Outstanding human follow-ups: placeholders, status, and either draft
     scaffold left standing — by name and item count, not its items.
   - `## Open questions`, when any remain
     ([references/proposals.md](references/proposals.md#open-questions)).
   - The decision-log line, only when anything was applied
     ([references/decision-log.md](references/decision-log.md#the-manifest-line)).
   - One start clause: what the draft check found, which delegates ran,
     whether the glossary resolved.

`autofix` owes this section only as
[references/autofix.md](references/autofix.md) step 8 states. `summary` owes
none of it: it applied nothing.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. Every count in the manifest — requirements
checked, edits applied, findings open, questions carried — is read off the
finished file, never carried from the work.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/srd/edit.md` (pass `~` as is, the
file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable. A missing file needs no comment. On a correction or self-caught
mistake, append a one-line rule — general, naming nothing from the project at
hand (its files, tests, tickets) — to the sibling when this directory is
writable, else to the fallback, creating it, and report where.
