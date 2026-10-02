---
name: backlog
description: >
  Works the open backlog of everything the documentation and the knowledge base
  still owe: questions deferred during SRD work, facts nobody has pinned down,
  and reported gaps in the user documentation. Use when asked to work the
  backlog, clear open questions, answer what was deferred, or write up reported
  documentation gaps.
argument-hint: "[all*|deferred|unknowns|gaps]"
license: MIT
---

# backlog

## Usage

```
/backlog           all three lists, cheap wins first (default)
/backlog deferred  questions someone knows the answer to; closed by asking
/backlog unknowns  things nobody has pinned down; triage, not answering
/backlog gaps      reported holes in the user manual; drafts the page
```

One sitting over the three lists the SRD skills fill as a byproduct, cheap wins
first.

| List        | Says                        | Closed by               |
|-------------|-----------------------------|-------------------------|
| `deferred`  | someone knows; no time then | asking, right now       |
| `unknowns`  | nobody has pinned it down   | deciding or finding out |
| `gaps`      | the user manual falls short | someone writing a page  |

A gap whose fact the KB states, with no page planned yet, is parked as `kb`:
out of the open backlog, still resolvable once a page is published.

The lists are not interchangeable: an unknown filed as a gap sits forever in a
backlog whose only tool is authorship, and a gap says nothing about what the
system is.

## Boundaries

- Role: the consumer end of every backlog — list, triage, extract, close.
- Must not: write any file under the `kb` folder (`srd:kb` owns it; every
  knowledge-base write, row move, or row edit is delegated there); publish to
  Confluence; author or edit an SRD; file new gaps (`srd:report-doc-gap` owns
  that).
- Depends on: `srd:kb` for the KB lists, the server's gap store for `gaps`.

## Sources of truth

- [../kb/references/retrieval-authoring.md](../kb/references/retrieval-authoring.md)
  (on-demand: drafting a page in `gaps`) — how to write Markdown the corpus
  chunks and ranks well. `srd:kb` owns it.
- [../create/references/project-config.md](../create/references/project-config.md)
  (eager) — the gate every sitting passes first, and the `kb` folder and
  server it names.
- [../create/references/doc-corpus.md](../create/references/doc-corpus.md)
  (on-demand: the first corpus lookup) — the server's tools and how to use
  them. `srd:create` owns it.

## Backends

The KB lists read `<kb>/_open-questions.md`, `kb` from `project-config.md`: one
row per question under `## Open` (label, kind `deferred` or `unknown`, date
raised, hit count, `Lives in` page link) or `## Closed`, which keeps the same
columns — `kind` included, so a closed row still says whether it had been a
deferred question or an unknown — plus the date closed and where the answer now
lives. The wording lives in the page's `## Open questions` section; a row with
an empty page link has only its label. When a question closes, its wording
leaves that section — the answer is on the page or in the inbox now, and a
question still posed beside its own answer reads as unresolved to the next
person — and when that was the last one, the heading goes too, since an empty
heading promises a list the page does not have.

The `gaps` list uses the server's gap tools on `mcp__<mcp-server>__`:
`list_gaps` (optional `status`), `mark_gap_kb` (`gap_id`, `kb_ref`, optional
`note`), `resolve_gap` (`gap_id`, `published_url`, optional `note`); the read
tools `search`, `get_doc`, `list_docs` come from the same server. An error from
a call is a store that exists and is unwell: report it with its message and
stop working `gaps`; never retry it or work around it.

A gap record carries `id`, `status`, `created_at`, `kind`
(missing/wrong/incomplete/ambiguous), `topic`, `doc_id`, `heading_path`,
`source_url`, `demand`, `target_claim`, `detail`, `search_terms`, `srd_ref`,
and, once parked, `kb_marked_at` and `kb_entry` (`ref`, `note`).
Empty `doc_id`/`heading_path`/`source_url` mean the reporter found nothing
relevant. Statuses: `draft`, `open`, `kb`, `resolved`, `duplicate`,
`wontfix`. A `draft` is still `srd:report-doc-gap`'s — never in this backlog.

## Workflow

The first token names one list, or `all` (default). Copy this checklist and
tick it off:

- [ ] 0. Pass the gate. Always, before anything below.
- [ ] 1. Open the sitting: count each list, stop for the user's pick. Skipped
      when a list was named.
- [ ] 2. `deferred`: ask, hand the answer to `srd:kb`.
- [ ] 3. `unknowns`: triage, never answer.
- [ ] 4. `gaps`: cluster, check the corpus, grill, draft, resolve or park.

Work one list at a time; a pick names one list, and when it is done offer the
next non-empty one. Close each item through its own mechanism, one call per
item.

### 1. Open the sitting

State the counts in one line and stop. Lead with `deferred` when it is
non-empty: a sitting that opens with quick closes keeps going. All three empty:
say the backlog is clear and stop.

### 2. deferred

Take the rows one at a time, in the order raised. Ask the question as worded on
its topic page, or from the row's label when it has no page yet.

- Answered: hand the fact to `srd:kb`, which writes it and moves the row to
  `## Closed` with the answer and the page that now states it.
- "Still not now": leave the row; do not re-ask it this sitting.
- No answer exists: it is an unknown, not a skip — have `srd:kb` change the
  row's kind in place, and say so.

### 3. unknowns

Only the user closes an unknown. You may read the corpus — an unknown that
turns out to be documented is worth knowing — but a hit is evidence to put in
front of them, never a closure. It is either about a different question, or the
very thing that should have closed this row long ago, and only they can say
which. Reading one as the answer is how an unknown gets closed with a guess
wearing a source. Bring the hit, name what it does and does not settle, and let
them decide.

For each row:

- Answered since (a decision was taken, or someone found out): hand the answer
  to `srd:kb`, which closes the row.
- Still open: confirm and move on. Bump nothing — the hit count tracks
  encounters during SRD work, not reviews.
- Moot (the feature changed, the subject went away): have `srd:kb` close the
  row saying why, so it is not re-opened.

Never invent an answer to close a row: an unknown left open is correct; one
closed with a guess is a fact the corpus will serve as truth.

### 4. gaps

Draft the page that fixes the user manual; a human publishes it.

1. List open gaps (`list_gaps` with `status: open`).
   `kb` gaps are not in it; list them with `status: kb` only when a page for
   one is being written or published.
2. Cluster the gaps one page would resolve — same `doc_id`, same
   `heading_path`, or one topic phrased differently. Rank by cluster size:
   repeated reports mean higher priority. The user picks one; work one at a
   time.
3. Check the corpus: `search` each gap's `search_terms`, `get_doc` any cited
   `doc_id`. Genuinely absent content needs new prose — added to the existing
   page when it is partly present there; present-but-unranked content needs a
   structural edit to the existing page, never a duplicate (the reference's
   "Absent vs unfindable").
4. Extract what the page must state. A record says what is missing, not what
   is true — but some were grilled at depth when filed and already carry
   knowledge in `detail` and `target_claim` (`srd:report-doc-gap` calls that a
   heavy grill). Spot them by a populated `target_claim`, read those first as a
   starting point, not gospel.
   Run `craft:grill-me` on the cluster to fill what the record leaves open,
   never re-asking what it answers. Do not draft from guesses: every sentence
   of the draft is something the user confirmed or the corpus states — a
   gap's own claim is the reporter's word until the user confirms it, and a
   draft states no consequence or summary neither source gave.
5. Draft one page (or the edit to an existing one) against
   [../kb/references/retrieval-authoring.md](../kb/references/retrieval-authoring.md),
   to a neutral drafts location the user names, outside every corpus source —
   the `kb` folder included: a draft inside a source is clobbered by the next
   sync and pollutes the index. The sources are the top-level folders the
   `list_docs` ids start with; unsure whether a path is outside them, ask.
6. Resolve once the human gives the published URL: `resolve_gap` for every gap
   in the cluster, so each moves from `open` or `kb` to `resolved` with the URL
   recorded. An edit to an existing page has a URL already — that page's — and
   it is the right one to record: the gap is closed by what the reader can now
   find there. When nobody can publish in this sitting, resolve nothing: say
   where the draft is and that the gaps stay `open` until it lands, since a gap
   resolved against an unpublished draft reads as done to everyone after. Say
   that the corpus reflects the page only after the next sync, plus a server
   restart unless the server watches its sources.
7. Park instead of steps 5–6 when the user decides the fact stays in the KB for
   now — no page planned this sitting. Only once `srd:kb` has written the
   section in a topic page under the `kb` folder: `mark_gap_kb` for every
   gap in the cluster, `kb_ref` the KB document ID plus anchor
   (`kb/users-and-access.md#customer-and-project-timezones`), `note` saying
   which decision parked it. Never park against `_inbox.md`: its anchors
   break on the next `/kb file`, and no skill can re-point a parked gap. Never
   park against an unconfirmed fact, nor a section that only partly covers the
   gap. Leave each such gap `open`.

A platform fact the grill surfaces also goes to `srd:kb`, unless this sitting
publishes a page that states it: the KB holds only what the docs do not. The
gap and the KB entry close independently.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. Counts and what closed are enough — never
re-print a drafted page or the rows just moved.

Name `srd:kb` as the writer whenever a row moved or a page changed, as a count
per delegate (`srd:kb: 2 answers`), never a list of files written or rows
moved: this skill writes nothing under the `kb` folder, and a report that says
"closed two" without saying who wrote them reads as though it did.

"What closed" is said once per sitting, in the closing line — not again as each
list finishes, and not restated in two shapes ("`gap-0010`, `gap-0015`
resolved" and "1 cluster closed (2 gaps)") in the same breath. Name parked gaps
apart from resolved ones (`gap-0003` parked as `kb`): a parked gap still owes a
page.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/srd/backlog.md`, the
sibling winning a conflict — a read-only install writes the second, and what it
learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule to the sibling when this directory
is writable, else to the fallback, creating it, and report where.