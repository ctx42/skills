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
/edit <srd> <srd>.review.md  feedback: apply a review file or pasted feedback, blocker → major → minor
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
mandate is reported, not looped — even when the run entered at it: a feedback
run starting at a metadata `#2` says so and advances to `#3`. An explicit `#n`
sets the order for the rest of the run, so advancing means the next number, not
a return to severity order — the user who named a number is reading the file by
number. It never proposes a Status
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
reuse them, never duplicate. **This skill depends on `../create/references/*`,
`../create/assets/*`, and `../create/scripts/*` — do not move or rename
`create`. If a referenced file is missing at run time, stop and tell the
user.**

- [../create/references/srd-standard.md](../create/references/srd-standard.md)
  (eager) — the rules (`STR`, `STA`, `LANG`, `REQ`, `GLO`, `SCO`, Quality Bar);
  every edit and check cites these ids.
- [../create/references/authoring-guide.md](../create/references/authoring-guide.md)
  (eager) — house extensions (US English, sub-numbering, one term per concept,
  the consistency pass) and the Bad→Good defect classes to fix toward.
- [../create/references/doc-corpus.md](../create/references/doc-corpus.md)
  (eager) — how to reach the documentation corpus, how its sources rank, and
  where an unconfirmed or undocumented fact goes.
- [../create/references/errata.md](../create/references/errata.md) (on-demand:
  autofix) — the gate, allowlist, and exclusions of the bulk-fix errata class.
- [../create/references/srd-procedures.md](../create/references/srd-procedures.md)
  (on-demand: session start for glossary resolution; Generate In Scope for the
  derivation procedure).
- [../create/assets/srd-template.md](../create/assets/srd-template.md)
  (on-demand: restructuring) — the required section order.
- [../create/scripts/glossary-fingerprint.sh](../create/scripts/glossary-fingerprint.sh)
  (run, not read) — hashes the Company Glossary so its term digest is rebuilt
  only on change; the digest keeps term edits linking, not redefining.

## Documentation corpus

Procedure, trust, and where an outcome goes:
[../create/references/doc-corpus.md](../create/references/doc-corpus.md). When
a new or changed requirement asserts something about existing system behavior,
`search` the corpus before accepting the edit; absent a corpus, edit offline.
Both delegates drain at session start and finish at session end. A platform
fact is attested through the edit-discipline loop's confirmation: a proposal
resting on it states that fact, so `Y`/`YN`/`E` attests it and `S` withholds
it; `srd:kb` may only sharpen a fact the edit already put in play. A deferred
question goes to the knowledge base's open-questions list through `srd:kb`, not
to this skill's `## Open questions`, which tracks questions about this SRD and
empties with the session.

## Session start (every mode)

Before any edit:

1. Read the whole SRD top to bottom.
2. Drain: invoke `srd:report-doc-gap` and `srd:kb` to surface what a prior
   session left buffered for this SRD.
3. Approval gate: read the `Status` metadata, pre-fill approved (`ACCEPTED`)
   vs in-progress (anything else), then show it and ask the user to confirm or
   override. The answer governs id rules for the whole session — never trust
   `Status` silently.
4. Glossary: run the glossary-resolution procedure in
   [../create/references/srd-procedures.md](../create/references/srd-procedures.md).

`autofix` runs only steps 1–2: errata never touches ids or terms.

## Id rules

On an approved SRD the gate governs content, not only ids. STA-4: adding,
removing, or changing a requirement needs the approving authority's agreement.
The user's `Y` is not that — it makes the edit the one they want, not one the
standard permits. So name STA-4 in the proposal and ask whether the authority
has agreed; without it, leave the edit marked for their ruling, unlanded. The
decision log records only applied edits and this skill writes no review file,
so an unlanded edit lives in the closing manifest or nowhere — list each with
its STA-4 ask.
Removal is the sharp case: STA-8 keeps the id and strikes the text, so "remove
GR-4" is never a deletion (STA-7 keeps the number). Meaning-preserving
editorial change is STA-5 and needs none of this — `polish` is that mode.

The gate then decides what may happen to requirement, scope, and glossary ids:

- In-progress: sub-number a split first — `GR-3` becoming `GR-3a`/`GR-3b` keeps
  every existing cross-reference working, which is why the authoring guide's
  own REQ-1 example does it. Renumbering the group is free here and is the
  right move when sub-numbering cannot express the change: an item crosses
  groups, or the numbering is already wrong (REQ-2/3/4 collisions and gaps).
  Update every cross-reference the change touches.
- Approved: existing ids are frozen. Additions only, via sub-numbering
  (`GR-1a`, `GR-1b`); never renumber or rename an existing id. A taken suffix
  moves down the alphabet — splitting `GR-3a` beside an existing `GR-3b` adds
  `GR-3c`. Never reuse a suffix, a struck-through one included: the id retires
  with its requirement. If a real fix
  cannot avoid touching an existing id, try add-only first; if that is
  impossible, present the conflict and the trade-off and leave it flagged
  unless the user explicitly approves the id change.

Whenever any id must change, state the change and get explicit approval as part
of the loop's confirmation. A renumbering pass excludes every comment block from
the substitution (comment text is verbatim history and may name an id that
never existed); verify afterwards that no comment line carries a new-scheme id.

## Edit discipline

When listing the issues found before the loop, keep only findings that survive
scrutiny: a real rule violation, not a preference. Requirements that read as
overlapping are often independently testable (a disabled control vs a grayed
one; a length cap vs its truncation format); a scope item covering one
capability across many surfaces is atomic; a compound term whose parts are in
the Company Glossary needs no entry. A finding withdrawn mid-session costs the
user's trust in the whole list.

Every mode but `autofix` runs this loop per change:

1. Propose exactly one change: its location/id, the problem (cite the rule id),
   the before and after text, and a one-line rationale.
2. Close the proposal with the choices (Yes / Yes Next / Skip / Edit) — the
   capital letter is the key — and apply only on explicit approval:
   - `Y` (Yes): apply, then stay on the current entry and propose its next
     issue; advance only once the entry is exhausted. In `feedback` the unit
     is the review's finding, not the entry, so `Y` proposes the next finding
     on that entry and stops when the review has no more — never an issue the
     review did not raise. Applying a review means applying that review.
   - `YN` (Yes Next): apply and move to the next entry, leaving its remaining
     issues flagged.
   - `S` (Skip): change nothing; leave the issue flagged.
   - `E` (Edit): apply the user's amended text in place of the proposal.
   Advance to the next entry only on `YN` or an explicit ask; once an entry is
   resolved, stop and wait, never walking ahead even for a read-only look.
   Never batch unrelated changes; never edit without confirmation. Ask one
   question at a time: never trail a proposal with loose questions or asides;
   anything held over goes in an `## Open questions` numbered list — one line
   each, no rationale — so the user answers by number ("1 yes, 2 skip"). That
   list is terminal output, not a section of the SRD: it belongs to this
   session, empties with it, and writing it into the document would leave
   questions behind for the next reader to mistake for content. Carry it
   forward in the conversation, renumbered from 1 each time you re-show it so
   answered items leave no holes, until it empties; what is still open at the
   end goes in the closing manifest.
3. Re-validate the affected entry and its cross-refs at once against the
   standard, focusing on what the edit can touch: scope coverage (SCO-2/3,
   suspended while the In Scope `--- TODO ---` marker stands), id
   uniqueness/order (REQ-3/4), term use (GLO-3), and any requirement that
   references or is referenced by the edit. Report a problem the fix
   introduced. When the edit asserts a claim about existing system behavior
   and a corpus is available, confirm it against the docs and route the
   outcome per [Documentation corpus](#documentation-corpus).
4. Log the change in `<srd>.decisions.md` before proposing the next one (see
   [Decision log](#decision-log)).

Write every edit to the LANG and REQ rules and the authoring guide (US English,
one term per concept); when an edit restructures sections, follow the
template's order.

## Decision log

`autofix` is a bulk path through the same gate, not an exception to it: every
substitution it applies is an applied edit and owes its entry, and
[references/autofix.md](references/autofix.md) is the procedure for finding and
applying them, not the whole of what the mode owes.

Record every applied edit in `<srd>.decisions.md` beside the source — the
author-facing account of what changed and why, which a diff cannot carry.

- Write after each applied edit, never batched to session end: a session that
  clears mid-flow must lose nothing.
- Accumulate: one file per SRD, `##` session blocks headed by the date, newest
  first. Never rewrite or prune an earlier block.
- Record the entry/id, the change in prose (not a diff), and the reason: the
  user's rationale when they gave one, the proposal's when it stood unamended.
- Rephrase the user's words into clean prose — fix typos, expand shorthand,
  drop the conversational frame — keeping decision and reason intact. Never
  invent a reason the user did not give.
- Every applied edit, loop or not: `autofix` logs one entry per substitution,
  Add-to-TODO logs its line. Same changes, same log.
- Skipped and flagged-but-unfixed issues are not logged: they stay in the
  review file, or — with none, since `edit` may not create one — in the closing
  manifest, which then says which were left and why.
- Write for the SRD's author, not a reviewer: name the surface in the SRD's own
  words; cite a rule id only where the user did.
- Create the file on the first write, frontmatter and title included;
  `cfsync-plugin: ignore-push` keeps the Confluence sync from pushing it.

Example of the file after one session — the date, heading, ids, and prose are
illustrative, not boilerplate to copy:

````
---
cfsync-plugin: ignore-push
---

# Changes — <Document Title>

## 2026-07-27

### Details page

DET-14 was removed. Retention and data accessibility are not part of this SRD,
so the requirement and its open "retention period to be confirmed" note went
with it. DET-13 still covers keeping historical measurements available after a
channel is reassigned.
````

## Draft scaffolds

Two working scaffolds live in a draft SRD (House additions in the authoring
guide). Maintain them across every mode and never remove either silently; both
block `ACCEPTED` and are reported as follow-ups at session end.

- In Scope `--- TODO ---` marker: while `### In Scope` holds only this marker,
  In Scope is knowingly pending — suppress every SCO-2 / In-Scope-coverage
  complaint (issue summary, re-validation, consistency pass) and do not
  fabricate `SC-n` items. Resolve it only via Generate In Scope below.
- `## TODO` section: a numbered list of open issues the human must return to,
  kept as the document's last section.

### Add to TODO (any time)

On "Add X to TODO" (or similar), append X as the next numbered item of
`## TODO`, creating the section last if absent. The instruction is the
confirmation: skip the loop, renumber nothing else, report only the line added.

### Generate In Scope (on the user's signal)

Only when the marker is present and the user signals the requirements are
complete (or asks to fill In Scope): run the In Scope derivation procedure in
[../create/references/srd-procedures.md](../create/references/srd-procedures.md)
and walk its candidate `SC-n` items through the loop, applying each confirmed
item. Replace the marker with the confirmed items, then re-run the SCO-2/3
check. Never trigger this on your own.

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
   its rule id. Edit nothing yet.
2. Walk entry by entry in document order — each requirement (`PFX-n`), glossary
   term, and scope item — running the loop for every fix the user approves.
   Move on only after the current entry is resolved or skipped.

Start point (path + line): resolve the line to the entry or paragraph at or
nearest it, skip step 1, and begin step 2 there, continuing to the end. The
walk is still one entry at a time and still never looks ahead — step 1's
summary is what would have told you which later entry has a finding, and
skipping it means learning that entry by entry. Say "no finding" and move on
for a clean one rather than scanning forward for the next interesting entry.

### feedback

Apply findings from a review; the review file stays untouched regardless of
outcome.

1. Input is a `<srd>.review.md` path or feedback pasted inline (email, ticket,
   chat); parse the findings from either.
2. Work findings in severity order — blocker → major → minor — using the
   review's tags and numbers; judge untagged pasted feedback from the rule.
3. Run the loop per finding; reference findings by number in the closing
   manifest.
4. Close by pointing the user to `review <srd> check` to reclassify what
   landed.

Start point (path + `#n`): requires an existing `<srd>.review.md`; if absent,
say so and stop. Enter at finding `#n` instead of severity order; after each
finding, default to the next by number or jump to any number the user names.

### autofix

Bulk-apply the `## Errata` block of `<srd>.review.md` behind one batch
confirmation — never the edit loop, never a re-scan of the SRD. The full
procedure is in [references/autofix.md](references/autofix.md) *(on-demand:
this mode only)*: read it before applying anything.

### polish

Mechanical-only cleanup through the loop, confirming each change. Scope:
British → US spelling, identifier format/order (REQ-2/3/4, subject to the
approval gate), keyword capitalization (LANG-4), valid Markdown, stray
example/note text (REQ-7), spacing and punctuation. Never rewrite requirement
meaning or restructure.

### targeted

Edit one entry the user points to by requirement id (`GR-3a`), quoted text, or
free description ("the login timeout rule").

1. Locate the target; for quoted text or a description, confirm the match
   before editing.
2. Run the loop on that entry.
3. Report the re-validation result explicitly: whether the edit introduced any
   inconsistency in the entry or its cross-refs.

## Session end (every mode)

1. Re-check the whole document against every rule in the standard plus the
   consistency pass in the authoring guide, and report what remains. `autofix`
   skips this step: its fixes are surface-only.
2. Invoke `srd:kb` to write the facts the session's confirmations attested,
   and `srd:report-doc-gap` to offer to work the gaps it buffered this
   session. `srd:kb` asks where the knowledge base lives when no root is on
   file, which on a first run lands here, just before the manifest. Resolve it
   at session start instead when the session has facts to bank: a setup
   question between the last edit and the closing report reads as an
   interruption of the report, and the answer is needed either way.
3. Close with the manifest — approved edits, not a re-narration of diffs the
   user already saw:
   - What changed: entry/id, one line each.
   - What was flagged and left (frozen-id conflicts, metadata gaps, anything
     the user declined).
   - Outstanding human follow-ups (placeholders, Status), including an
     unresolved In Scope `--- TODO ---` marker and any non-empty `## TODO`
     section — both block `ACCEPTED`.
   - The path to `<srd>.decisions.md`, whose newest session block is the
     summary to hand the author.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md`
and `$HOME/.agent-data/ctx42-skills/lessons/srd/edit.md`, the sibling winning
a conflict — a read-only install writes the second, and what it learned there
stays true once the checkout is writable again. Most runs have none; absence
is the normal case and needs no comment. On a correction or self-caught
mistake, append a one-line rule to the sibling when this directory is
writable, else to the fallback, creating it, and report where.