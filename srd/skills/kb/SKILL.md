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
/kb                 capture (default): confirm, write to the inbox
/kb capture <srd>   capture for one SRD, by its path
/kb file            file inbox facts into topic pages
/kb restructure     reorganize pages and repair every reference
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

### Authority

The shared corpus reference settles conflicting sources by the `rank` on each
result, never by folder. Three consequences for KB writes:

- A conflict is a finding, never a silent tie-break. When an attested fact
  contradicts a platform document (not a KB section — see below), either the
  document is stale or the KB is wrong. Surface it; hand a stale document to
  `srd:report-doc-gap`. A fact the user confirmed against it is written without
  a further question, its attestation line opening
  ``> Contradicts `<identity>`.`` (the document's `id`) in place of
  `> Not in the platform docs.` — whether the conflict was known at
  confirmation or turned up after it, at write time: a fact written while a
  document says otherwise always carries the line.
- A KB page links to a glossary term; it never redefines one.
- A KB section and an SRD never contradict, and no `rank` settles one that
  does: an SRD has none. A confirmed fact rewrites the section it contradicts
  at once (step C.1): the KB changes on confirmation, not when other SRDs
  agree.

## Invocation

Every mode runs the gate first. The first token is a mode word; the next is the
SRD path when one is in play. Callers pass both. With no arguments, default to
capture.

An SRD path the conversation states counts as named. With no SRD named and
no caller to name one, the session itself is the source:
take what this conversation attested and attest it to the session rather than
to an SRD — do not infer an id from the conversation to fill the slot, which
invents a provenance nobody can check. The `*` in the argument hint marks the
default, here and in every skill that carries one.

- `capture` (default) — confirm and write what the session surfaced. The flow
  below.
- `file` — move inbox facts into topic pages. See [File](#file).
- `restructure` — reorganize the KB and repair every reference. See
  [Restructure](#restructure).

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
to `srd:report-doc-gap` as a gap with `answer: deferred` (see
[Open questions](#open-questions)) and move on immediately. Never re-ask in the
same session.

### C. Write to the inbox

A caller may also hand over a stale citation: a KB page citing an identity no
`list_docs` `id` or `path` matches. Repair it in place (re-find the document by
`search` and cite its `id`, or drop the citation and mark the fact as attested
only) and report the page.

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
   heading, the attestation line (see [Page anatomy](#page-anatomy)), the
   fact — and its row in the inbox's `## Provenance` table. The inbox's front
   matter carries `title` and `last_verified`
   (each write bumps it), never `srd_ref`: each section's attestation line
   names its source. Create the file that way when missing.
   Never to a topic page or a category invented at this moment: filing is
   [File](#file)'s job. The inbox is indexed and retrievable, so nothing waits
   on a filing decision.
3. Write per [references/retrieval-authoring.md](references/retrieval-authoring.md)
   and the body rules in [Page anatomy](#page-anatomy).

## File

`/kb file` moves inbox facts to where they rank. A fact in the inbox inherits
the inbox's title field, which says nothing about its subject, so it ranks far
below the same fact on a subject-titled page (a fact absent from the top 10 for
its own query reaches rank 1 after promotion). Offer it whenever the inbox
holds a fact a topic page would take.

1. For each inbox section, find the topic page whose subject contains it; when
   one does, propose moving the section there.
2. When **two or more** inbox facts share a subject no page covers, propose
   creating the top-level page and moving them in. A single fact never earns a
   page — it stays in the inbox, better found under a subject heading than
   alone on a page of its own. That rule governs filing only, not
   [Restructure](#restructure), which moves sections that already have a home
   because the home turned out wrong; there, one section may be exactly what
   moves.
3. Show the proposed moves and get confirmation before touching anything.
4. Move each section with everything bound to it and repair every reference
   the move breaks, as [references/restructure.md](references/restructure.md)
   steps 2–3 say: a moved section's identity changes (a KB page's identity is
   its path), and gap `doc_id` values and `filled_by` refs may point at it.
5. Report what moved where, counted.

Append by default. Two half-pages on one subject are strictly worse than one
fat page: scattered names split matches, so both rank below where one would.
When in doubt, append.

Never split a page to fix its size. A KB page's identity is its path, so a
split breaks every citation to it. A page that has grown large is fine; the next
related subject gets a sibling page instead.

## Page anatomy

One page per subject, many `##` sections per page. Only `#` and `##` start a new
chunk, so `##` is the unit that reaches an agent alone.

Front matter:

```yaml
---
title: Acoustic Leak Detection
aliases: [AUTOCO, automated cross-correlation]
attested: 2026-09-11
srd_ref: int384-hydrophone, autoco
last_verified: 2026-09-11
---
```

`srd_ref` accumulates: a page attested across several SRDs lists their SRD
references (folder names, per the gate reference) comma-separated,
earliest first, and a write appends rather than replaces.
`attested` stays the first date; `last_verified` moves.

`title` is always explicit — without it the indexer falls back to the file name.
`aliases` carry abbreviations and synonyms; they index at the title's boost on
every section of the page, so a search for the short form finds it. The
remaining keys are for humans and staleness sweeps; the indexer ignores them.

Body rules:

- The body states attested facts only. Anything the agent concluded but the
  user did not confirm never enters it — that is an open question, not a fact.
  This rule alone keeps a large KB trustworthy. After each write, re-read the
  page and delete every sentence no attested statement says, a consequence or
  generalization of the fact included; a sentence meant to be cut is cut only
  once the file no longer holds it.
- Mark tribal sections in place. A section carrying something the platform
  docs do not state opens with one line under its heading, so the mark travels
  inside the chunk:

  ```
  > Not in the platform docs. Attested int384-hydrophone interview
  > 2026-09-11 · `gap-0019`.
  ```

  The source (the SRD reference) and the date are required; a document the
  line cites is an inline-code identity (`` `1774485611#tag-names` ``), never
  a path the document only has today; the `· gap-NNNN` is there only when
  `srd:report-doc-gap` actually filed one and returned an id. Most captures
  have none — a fact can be missing from the docs without anyone reporting
  that as a gap — so omit the segment rather than inventing a number or
  holding the write until a gap exists. When a gap for the fact is filed
  later in the same session, add its id to the line then. Where there is no
  SRD in play (a bare capture, a `/backlog` sitting), name the session
  instead: `Attested session 2026-09-11`.

  A page-level provenance table cannot do this job: it is its own chunk, and an
  agent reading a fact never receives it.

- `## Provenance` closes the page as a human-facing roll-up — which areas
  rest on documents, which on a conversation. An index, not the mechanism.
  Every write adds or updates its row there, whether the write creates the
  page or appends a section to one: a roll-up nobody maintains indexes a page
  that has moved on. A citation repair updates the row of the fact it
  repairs; it adds none. A page with no `## Provenance` yet gets one on the
  first write that touches it. The inbox keeps one too, and a section filed
  out of it carries its row along.
- A page states no open question: what its subject leaves unanswered is a gap.
  See [Open questions](#open-questions) below.

## Open questions

A question SRD work leaves open is a gap in the server's store, never a KB
write. Its `answer` says which kind: `deferred` — someone knows, the session
did not take it; closable in seconds. `unknown` — nobody has pinned it down; it
needs deciding or finding out.

A guess of your own that the user never confirmed is `deferred`, not `unknown`:
the user was there and could have settled it, and calling it an unknown puts
the agent's inference on the same footing as a fact nobody in the organization
has. State it as the question it answers ("does evidence expire, and after how
long?"), never as the inference wearing a question mark.

A user who does not know the answer:
[Who would know](../create/references/doc-corpus.md#who-would-know).

File it through `srd:report-doc-gap` with `answer` set; it dedups with
`list_gaps` `query`, and a question already on file gets a hit
(`update_gap` `add_hit: true`), never a second record. Repeats are a priority
signal.

A KB page, the inbox included, keeps at most a point-of-use warning: one line
after the attestation line of the section the question concerns,
`> Open: gap-0042.`, naming the filed gap's id — never the question's wording,
which lives on the gap alone. Add it only once the gap is filed (a draft's id
can vanish); delete it when the section comes to state the answer.

`srd:backlog` works these gaps and hands each answer here like any caller.

## Restructure

Splitting a page, moving a section between pages, or renaming a subject is a
restructure: confirm it first, then repair every reference it breaks — links,
heading slugs, and gap-store `doc_id` and `filled_by` values. The
procedure is in [references/restructure.md](references/restructure.md), read
when a write would restructure rather than append.

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

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/srd/kb.md`, the
sibling winning a conflict — a read-only install writes the second, and what it
learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule — general, naming nothing from
the project at hand (its files, tests, tickets) — to the sibling when this
directory is writable, else to the fallback, creating it, and report where.