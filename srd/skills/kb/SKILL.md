---
name: kb
description: >
  Captures durable platform knowledge into the project knowledge base as a
  byproduct of SRD work, and keeps that knowledge base coherent and
  retrievable. Use when an SRD interview surfaces a fact the documentation
  does not carry, when banking what a session taught about the platform, or
  when reorganizing the knowledge base.
argument-hint: "[capture*|file|restructure] [<srd path>]"
license: MIT
---

# kb

## Usage

```
/srd:kb                 capture (default): confirm, write to the inbox
/srd:kb capture <srd>   capture for one SRD, by its path
/srd:kb file            file inbox facts into topic pages
/srd:kb restructure     reorganize pages and repair every reference
```

Rarely invoked by hand: `srd:create` and `srd:edit` call it themselves,
`srd:system-check learn` banks what a non-SRD conversation taught, and
`srd:backlog` hands it every answer a backlog sitting takes.
Reach for it directly to file the inbox, to restructure, or to work a session's
facts with no SRD skill driving.

Single owner of the **knowledge base** (KB): Markdown pages stating what the
platform *is* — rules, entities, behavior of the target system the SRDs also
describe, and never contradict — written by the agent from what the
user attests during SRD work, and served back to every agent through the
corpus. It exists because such knowledge has nowhere else to live: not in the
platform docs (that is what makes it tribal), otherwise only in a
`<srd>.questions.md` that empties as questions resolve, or in one person's
memory.

## Boundaries

- Role: the single knowledge-base handler. Write what the user attests, keep
  the pages coherent and findable.
- Owns: every file under the `kb` folder. No other skill writes there.
- Must not: run `git` — the agent writes the working tree, the user commits;
  write outside the `kb` folder, ever; file documentation gaps (that is
  `srd:report-doc-gap`); author or edit an SRD (`srd:create`, `srd:edit`);
  publish anything outside the repo; write a fact the user has not confirmed;
  keep anything in per-machine state.
- Depends on: the corpus read tools for dedup and coverage checks. A KB hit
  is one whose `path` lies under the `kb` folder, and the index can lag the
  files. A hit there is evidence a page existed, not that it does now:
  resolve every hit to its file (`<project root>/<path>`) before appending to
  it; a hit with no file behind it is a new section to write, not a page to
  extend, however well its text matches.

## Support files

- [../create/references/project-config.md](../create/references/project-config.md)
  (eager) — the gate every mode passes first, and the `kb` folder, project
  root, and server it names.
- [../create/references/doc-corpus.md](../create/references/doc-corpus.md)
  (eager) — how to reach the corpus, how its sources rank, and the
  confirm / write contract every caller relies on.
- [references/retrieval-authoring.md](references/retrieval-authoring.md)
  (on-demand: before writing or editing a page) — how to write Markdown that
  the BM25 corpus chunks and ranks well. Mirrors the server README's
  *Writing documents that search well*; every page obeys it.

## The KB folder

The KB is the `kb` folder in `project-config.md`, relative to the project root;
the gate resolves it, so nothing is asked and nothing is remembered. One file
there is fixed: `_inbox.md`, where every confirmed fact lands first.

Hard rule: every write lands under the `kb` folder — a path outside it is
refused, never written. Read no sync, editor, or vault config to decide where
or whether to write: the gate's `kb` value is the only answer.

## The corpus

The KB is one source in the corpus the other SRD skills read. Two facts about
it govern every decision below. **A page written now is searchable only after a
re-index**: a server with watching enabled rebuilds shortly after a change,
one without never re-reads its sources until restarted. Verify a write with
`search` rather than assuming; when a just-written page does not appear,
re-check once, then say a restart may be needed — never conclude the page is
missing. And **search returns sections, not pages**: a `##` section arrives at
an agent alone, stripped of the rest of its file. Anything a reader must know
to trust a fact has to sit inside the same section.

Conflicting sources settle by `rank`, never by folder, and a conflict is a
finding, never a silent tie-break; a confirmed fact rewrites a KB section it
contradicts at once. A KB page links to a glossary term; it never redefines
one. [references/conflicts.md](references/conflicts.md) (on-demand: a fact
contradicts a platform document, a KB section, or an SRD; a caller hands over
a stale citation) — the `> Contradicts` line, SRD conflicts, citation repair.

## Invocation

Every mode runs the gate first. A mode word and, when one is in play, an SRD
path, in any order; callers pass both. With no arguments, default to capture.

An SRD path the conversation states counts as named. With no SRD named and
no caller to name one, the session itself is the source:
take what this conversation attested and attest it to the session rather than
to an SRD — do not infer an id from the conversation to fill the slot, which
invents a provenance nobody can check.

- `capture` (default) — confirm and write what the session surfaced. The flow
  below.
- `file` — move inbox facts into topic pages; offer it whenever the inbox
  holds a fact a topic page would take. Append by default, never split a page
  for size, and give no single fact a page of its own:
  [references/restructure.md](references/restructure.md) `## File`
  (on-demand: `file` mode).
- `restructure` — reorganize the KB. Splitting a page, moving a section
  between pages, or renaming a subject is a restructure: confirm it first,
  then repair every reference it breaks — links, heading slugs, and gap-store
  `doc_id` and `filled_by` values. The procedure is in
  [references/restructure.md](references/restructure.md), read in this mode
  and when a write would restructure rather than append.

A `key=value` that names no control here, or a word left over once the modes,
the target, and any text the skill takes are read: say it was not recognized,
name the ones that exist, and run with the defaults as if it were absent —
unless dropping it would widen what the run changes; then ask. A target that
resolves to nothing: say so and ask — never guess what to work on.

## Workflow

Callers (`srd:create`, `srd:edit`, `srd:system-check`, `srd:backlog`) hand a
fact over **once it is confirmed** — confirmation rides on the caller's own
confirmation step. Nothing is buffered: an unconfirmed candidate lives only in
the conversation, and a confirmed one is on disk in `_inbox.md` before the
caller moves on.

- [ ] A. On discovery: note the candidate in the conversation; no write, no
      interruption.
- [ ] B. At the caller's confirmation step: confirm the facts inside what the
      caller already restates or proposes.
- [ ] C. On confirmation: write each confirmed fact to `<kb>/_inbox.md`.

### A. Discovery

A candidate is a fact about the platform that the corpus does not carry and the
user has stated or confirmed. Note it — the fact in one line, its subject, the
SRD path, and the `id` of any result the lookup that exposed the gap returned —
and return: no user interruption, no corpus call, no write. One candidate per
**distinct** fact.

Not a candidate: anything the agent inferred but the user did not confirm;
anything specific to this SRD, ticket, or review rather than to the platform; a
restatement of the SRD under work. A deficiency in the *documentation* is a doc
gap for `srd:report-doc-gap`, not a KB candidate — though one fact may be both,
since the KB states it now and the gap stays open until a topic page or pulled
doc page states it.

### B. Confirm at the caller's confirmation step

Confirmation rides on a step the caller already performs — a branch
restatement in `srd:create`, a one-change proposal in `srd:edit` — never a
separate step, a separate question, or a "bank this?" prompt. The user must
not experience a knowledge-base track running beside the interview.

When the caller restates or proposes, fold the session's platform facts into
that text in natural prose. The user confirming it confirms the facts. A
correction corrects both.

A question may be asked purely to make a fact worth writing — values of a
status, the unit of a threshold, which of two names is canonical. It must sound
like the rest of the interview, and it may only **deepen a subject the
interview already opened, never open a new one**. A fact that would round out
the KB nicely, on a subject this SRD never went near, is not a reason to ask.

The user may wave off any such question with a word. Nothing is lost: hand it
to `srd:report-doc-gap` as a gap with `answer: deferred` and move on
immediately. Never re-ask in the same session. Filing it: `## Open questions`
in [references/page-anatomy.md](references/page-anatomy.md).

### C. Write to the inbox

A caller may also hand over a stale citation; repair it per
[references/conflicts.md](references/conflicts.md) and report the page.

For each confirmed fact, in order:

1. Search before writing — here, after confirmation, never at discovery; a
   lookup the caller ran during its interview does not count. Query the
   corpus for the fact's own words. The first case that matches decides:
   - A KB section states otherwise — even when the platform docs already state
     the confirmed fact: rewrite that section with the confirmed fact now, in
     place, its attestation line naming only this source (the SRD, or
     `session`) and date (`> Contradicts` only when a platform document still
     says otherwise); page front matter updates as for any write. Whatever
     this write's source, the report adds one line naming every SRD the old
     line named other than this one — each now contradicts the KB, a finding
     for its author; none named, no line.
   - The platform docs already state it — do **not** write. It is not tribal.
     If the docs state it *wrongly*, that is a doc gap, not a KB entry.
   - A KB page or inbox section already states it — do not write a twin. Add
     the SRD and date to the section's attestation line when the source
     differs; on a page also bump `last_verified` and append the SRD to
     `srd_ref`, in the inbox also update its `## Provenance` row.
   - Otherwise it is new.
2. Append it to `<kb>/_inbox.md` as its own `##` section: a subject-titled
   heading, the attestation line, the fact — and its row in the inbox's
   `## Provenance` table. The inbox's front matter carries `title` and
   `last_verified` (each write bumps it), never `srd_ref`: each section's
   attestation line names its source. Create the file that way when missing.
   Never to a topic page or a category invented at this moment: filing is
   `file` mode's job. The inbox is indexed and retrievable, so nothing waits
   on a filing decision.
3. Write per [references/retrieval-authoring.md](references/retrieval-authoring.md)
   and [references/page-anatomy.md](references/page-anatomy.md) (on-demand:
   before every write, and when a question stays open) — front matter, the
   attestation line every section opens with, the `## Provenance` row, the
   `> Open:` warning, filing an open question; the body holds only what the
   user attested.

## Output

Report tersely in every mode, capture included: no preamble or narration;
state each fact once; don't restate output the user can already see. One
pointer line per page touched, with its count — `kb/correlation.md: 2
sections` — is the report. Never what the facts say (the page holds them),
never a re-printed page, and nothing on how the write was done (searches,
provenance rows, re-indexing, sync) unless it needs the user to act — a
rewrite's contradicting SRDs do, one line (session-attested rewrites
included): `now contradicts the KB: specs/sso.md`. Wrong:
"`kb/logger.md` now has the battery-low threshold (15 %)". Right:
"`kb/logger.md`: 1 section".

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/srd/kb.md` (pass `~` as is, the
file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable. A missing file needs no comment. On a correction or self-caught
mistake, append a one-line rule — general, naming nothing from the project at
hand (its files, tests, tickets) — to the sibling when this directory is
writable, else to the fallback, creating it, and report where.
