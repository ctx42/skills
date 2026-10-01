---
name: kb
description: >
  Captures durable platform knowledge into the project knowledge base as a
  byproduct of SRD work, and keeps that knowledge base coherent and
  retrievable. Use when an SRD interview surfaces a fact the documentation
  does not carry, when banking what a session taught about the platform, or
  when reorganizing the knowledge base.
argument-hint: "[capture*|restructure] [<srd path or id>]"
license: MIT
---

# kb

## Usage

```
/kb                 capture (default): drain, confirm, write
/kb capture <srd>   capture for one SRD, by its path
/kb restructure     reorganize pages and repair every reference
```

Rarely invoked by hand: `srd:create` and `srd:edit` call it themselves,
`srd:system-check learn` banks what a non-SRD conversation taught, and
`srd:backlog` hands it every answered, moot, or reclassified open question.
Reach for it directly only to restructure, or to work a session's captures with
no SRD skill driving.

Single owner of the **knowledge base** (KB): Markdown pages stating what the
platform *is* — rules, entities, behavior — written by the agent from what the
user attests during SRD work, and served back to every agent through the
`srd-doc` corpus. It exists because such knowledge has nowhere else to live:
not in the platform docs (that is what makes it tribal), otherwise only in a
`<srd>.questions.md` that empties as questions resolve, or in one person's
memory.

## Boundaries

- Role: the single knowledge-base handler. Capture what the user attests,
  buffer it, write and maintain the pages, keep them findable.
- Owns: every file under the KB root. No other skill writes there.
- Must not: run `git` — the agent writes the working tree, the user commits;
  write outside the KB root, ever; file documentation gaps (that is
  `srd:report-doc-gap`); author or edit an SRD (`srd:create`, `srd:edit`);
  publish anything to Confluence; write a fact the user has not confirmed.
- Depends on: the `srd-doc` corpus read tools for dedup and coverage checks.
  The corpus indexes the knowledge base under its own `kb/` prefix, and that
  index can lag or outlive the files, and it may be indexing a different
  knowledge base than the root resolved here — the corpus serves whatever the
  server was built over, not whatever this machine points at. Either way a hit
  under `kb/` is evidence a page existed somewhere, not that it is in this KB
  root now. Resolve every hit to a real path under the root before appending
  to it; a hit with no file behind it is a new page to write, not a page to
  extend, however well its text matches.
  Without them, capture still works but every write is blind — say so and
  prefer the inbox over creating a page.

## Support files

- [../create/references/doc-corpus.md](../create/references/doc-corpus.md)
  (eager) — how to reach the `srd-doc` corpus, how its sources rank, and the
  drain / buffer / confirm / write contract every caller relies on.
- [references/retrieval-authoring.md](references/retrieval-authoring.md)
  (on-demand: before writing or editing a page, never on capture) — how to
  write Markdown that the BM25 corpus chunks and ranks well. Mirrors the
  server's own `docs/authoring.md`; every page obeys it.

## The KB root

The KB is **user data on this machine**, not shipped content, so its path is
resolved, never assumed. Resolve it once per run:

```bash
MEM_DIR="${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/srd"
mkdir -p "$MEM_DIR"
KB_ROOT="$(cat "$MEM_DIR/kb-root" 2>/dev/null)"   # absolute path to the KB dir
```

`AGENT_DATA_DIR` exists so a sandbox, a test, or an eval can point the store
somewhere disposable; with it unset the default is the real one. Read it the
same way everywhere — a run that honors it for reading and not for writing
leaves state in two places.

Empty or missing: ask the user for the directory, then write it to
`$MEM_DIR/kb-root`. Ask once per usable answer, not once per session: a path
that fails a check below is not an answer, so say why and ask again. The
"once" is about not re-asking for a root already on file, never about
accepting a bad one because the question was already spent.

- It is **not** managed by a Confluence sync. A sync pull clobbers agent writes
  and the page silently reverts. Check the sync config (`.cfsync.yaml` or
  equivalent) at the repo root: the KB directory must appear in no mapping.
  A path that fails this check is a data-loss bug, not a preference: refuse
  it and never write to it.
- It is a directory inside a git repository, so a bad write is recoverable.
  Warn — do not refuse — if the directory is untracked or the repo has no
  remote; say which, once.

## The corpus

The KB is one source in the `srd-doc` corpus the other SRD skills read; reach
it per the backends in the shared corpus reference. Two facts about it govern
every decision below. **A running server never re-reads its sources**, so a
page written now is not searchable until the server restarts — say so once
when it matters, and never conclude a page is missing because a just-written
page does not appear. And **search returns sections, not pages**: a `##`
section arrives at an agent alone, stripped of the rest of its file. Anything
a reader must know to trust a fact has to sit inside the same section.

### Authority

The shared corpus reference sets the trust order (the KB leads on how the
system behaves, the glossary on what a term means). Two consequences for KB
writes:

- A conflict is a finding, never a silent tie-break. When an attested fact
  contradicts a corpus document, either the document is stale or the KB is
  wrong. Surface it; hand a stale document to `srd:report-doc-gap`.
- A KB page links to a glossary term; it never redefines one.

## Invocation

The first token is a mode word; the next is the SRD path or id when one is in
play. Callers pass both. With no arguments, default to capture.

With no SRD named and no caller to name one, there is no per-SRD buffer to
drain: the session itself is the source. Take what this conversation attested,
buffer it under the session, and attest it to the session rather than to an SRD
— do not infer an id from the conversation to fill the slot, which invents a
provenance nobody can check. The `*` in the argument hint marks the default,
here and in every skill that carries one.

- `capture` (default) — buffer, confirm, and write what the session
  surfaced. The flow below.
- `restructure` — reorganize the KB and repair every reference. See
  [Restructure](#restructure).

## Workflow

Callers (`srd:create`, `srd:edit`, `srd:system-check`, `srd:backlog`) invoke
this skill **at start** (drain), **on discovery** (capture), and **when they
finish** (write); confirmation rides on the caller's own confirmation step in
between.

- [ ] A. On the caller's start: drain the buffer for this SRD.
- [ ] B. On discovery: buffer the candidate silently, no interruption.
- [ ] C. At the caller's confirmation step: confirm the facts inside what the
      caller already restates or proposes.
- [ ] D. When the caller finishes (its write or report step) — or at once when
      a caller hands over facts it has already confirmed — write each
      confirmed fact to the KB and drop it from the buffer.

### A. Drain

Read this SRD's buffer on the caller's start — a prior session may have cleared
with candidates unwritten.

Empty: tell the caller so and show the user nothing — the caller states in its
own report that the drain ran and was empty, which is not this skill's line to
write and not a silence either. Otherwise name the count and topics
and offer to work them now. Never force it; on defer they stay buffered.

Buffer location `$MEM_DIR/kb/<key>.json`, keyed by the SRD's path exactly as
`srd:report-doc-gap` keys its buffer (`_session.json` when no SRD is in play,
as in `system-check learn`, or none is written yet). Buffered means
unconfirmed. A candidate is removed on write or discard, and the file is
deleted when it empties.

### B. Capture on discovery

A candidate is a fact about the platform that the corpus does not carry and the
user has stated or confirmed. Write it to the buffer at once and return: no user
interruption, no corpus call, no page write.

Record what is free at this moment — the fact in one line, the subject it
belongs to, the SRD id, and any `doc_id` the lookup that exposed the gap
returned. Nothing else. One record per **distinct** fact: if the same fact is
already buffered for this SRD, merge rather than duplicate.

Not a candidate: anything the agent inferred but the user did not confirm;
anything specific to this SRD, ticket, or review rather than to the platform; a
restatement of the SRD under work. A deficiency in the *documentation* is a doc
gap for `srd:report-doc-gap`, not a KB candidate — though one fact may be both,
since the KB states it now and the gap records that the docs should eventually
carry it.

### C. Confirm at the caller's confirmation step

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

The user may wave off any such question with a word. Nothing is lost: route it
to `_open-questions.md` marked `deferred` and move on immediately. Never re-ask
in the same session.

### D. Write

A caller may also hand over a stale citation: a KB page citing a corpus id
absent from `list_docs`. Repair it in place (re-find the document by `search`,
or drop the citation and mark the fact as attested only) and report the page.

For each confirmed fact, in order:

1. Search before writing. Query the corpus for the fact's own words. Three
   outcomes:
   - The platform docs already state it — do **not** write. It is not tribal.
     If the docs state it *wrongly*, that is a doc gap, not a KB page.
   - A KB page already covers the subject — add or update a `##` section there.
   - Nothing covers it — it is new. Go to step 2.
2. Place it. A fact belongs to the KB page whose subject contains it. When no
   page does, write it to `_inbox.md` — never to a category invented at this
   moment. The inbox is indexed and retrievable, so nothing waits on a filing
   decision.
3. Write the section per [Page anatomy](#page-anatomy) and
   [references/retrieval-authoring.md](references/retrieval-authoring.md).
4. Promote when earned. When **two or more** inbox facts share a subject,
   create the top-level page, move them in, remove them from the inbox, and say
   what was created. A single fact never earns a page — that rule governs
   promotion out of the inbox, where a lone fact is better found under a
   subject heading than alone on a page of its own. It does not govern
   `restructure`, which moves sections that already have a home because the
   home turned out to be the wrong one; there, one section may be exactly what
   moves.

The inbox is staging, not storage. A fact there inherits the inbox's title
field, which says nothing about its subject, so it ranks far below the same fact
on a subject-titled page (a fact absent from the top 10 for its own query
reaches rank 1 after promotion). Promotion is what makes a fact findable; drain
the inbox at every opportunity.

Append by default. Two half-pages on one subject are strictly worse than one
fat page: scattered names split matches, so both rank below where one would.
When in doubt, append.

Never split a page to fix its size. The document id is its path, so a split
breaks every citation to it. A page that has grown large is fine; the next
related subject gets a sibling page instead.

## Page anatomy

One page per subject, many `##` sections per page. Only `#` and `##` start a new
chunk, so `##` is the unit that reaches an agent alone.

Front matter:

```yaml
---
title: Acoustic Leak Detection
aliases: [AUTOCO, automated cross-correlation]
cfsync-plugin: ignore-push
attested: 2026-09-11
srd_ref: INT-384, INT-392
last_verified: 2026-09-11
---
```

`srd_ref` accumulates: a page attested across several SRDs lists them
comma-separated, earliest first, and a write appends rather than replaces.
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
  > Not in the platform docs. Attested INT-384 interview 2026-09-11 ·
  > `gap-0019`.
  ```

  The source and the date are required; the `· gap-NNNN` is there only when
  `srd:report-doc-gap` actually filed one and returned an id. Most captures
  have none — a fact can be missing from the docs without anyone reporting
  that as a gap — so omit the segment rather than inventing a number or
  holding the write until a gap exists. Where there is no SRD in play (a bare
  capture), name the session instead: `Attested session 2026-09-11`.

  A page-level provenance table cannot do this job: it is its own chunk, and an
  agent reading a fact never receives it.

- `## Provenance` closes the page as a human-facing roll-up — which areas
  rest on documents, which on a conversation. An index, not the mechanism.
  Every write adds or updates its row there, whether the write creates the
  page or appends a section to one: a roll-up nobody maintains indexes a page
  that has moved on. A citation repair updates the row of the fact it
  repairs; it adds none. A page with no `## Provenance` yet gets one on the first
  write that touches it.
- `## Open questions` holds what this page's subject leaves unanswered. See
  [Open questions](#open-questions) below.

## Open questions

Two kinds, worked differently. `deferred` — someone knows, the session did not
have time to take it; closable in seconds. `unknown` — nobody has pinned it
down; it needs deciding or finding out.

A guess of your own that the user never confirmed is `deferred`, not `unknown`:
the user was there and could have settled it, and calling it an unknown puts
the agent's inference on the same footing as a fact nobody in the organization
has. State it as the question it answers ("does evidence expire, and after how
long?"), never as the inference wearing a question mark.

An unknown is **never** filed as a documentation gap. A gap's resolver is
someone writing a page; an unknown's resolver is someone finding out. Filed as a
gap it sits forever in a backlog whose only tool is authorship.

Each question lives in **two** places, with one owner:

- Its topic page's `## Open questions` section carries the **wording**. That is
  where an agent meets it at the point of use and is warned off guessing.
- `_open-questions.md` carries a **row** — short label, kind, date raised, hit
  count, link to the page. It is the list view, and it holds only a label, so
  the two copies cannot drift.

A question whose subject has no page yet lives in the index alone, with an empty
page link, until a page exists to take it.

On meeting a question that is already open, **bump its hit count** rather than
adding a row: repeats are a priority signal, the same way repeated gap reports
are. On closing one, move the row to `## Closed` with the answer and the page
that now states it, so the next session does not re-open it.

`srd:backlog` works this list and hands every row change here: close a row as
answered (with the answer and the page) or as moot (with the reason), or change
its kind between `deferred` and `unknown`. Apply the change as above without
re-confirming what backlog already confirmed with the user.

## Restructure

Splitting a page, moving a section between pages, or renaming a subject is a
restructure: confirm it first, then repair every reference it breaks — links,
anchors, `_open-questions.md` rows, and gap-store `doc_id` values. The
procedure is in [references/restructure.md](references/restructure.md), read
when a write would restructure rather than append.

## Output

Report tersely in every mode, capture included: no preamble or narration;
state each fact once; don't restate output the user can already see. A pointer
("wrote `kb/correlation.md`, 2 sections") is enough — never re-print a page
just written.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/srd/kb.md`, the
sibling winning a conflict — a read-only install writes the second, and what it
learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule to the sibling when this directory
is writable, else to the fallback, creating it, and report where.