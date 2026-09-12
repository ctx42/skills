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

The lists are not interchangeable: an unknown filed as a gap sits forever in a
backlog whose only tool is authorship, and a gap says nothing about what the
system is.

## Boundaries

- Role: the consumer end of every backlog — list, triage, extract, close.
- Must not: write any file under the KB root (`srd:kb` owns it; every
  knowledge-base write, row move, or row edit is delegated there); publish to
  Confluence; author or edit an SRD; file new gaps (`srd:report-doc-gap` owns
  that).
- Depends on: `srd:kb` for the KB lists, the `srd-doc` gap store for `gaps`.

## Sources of truth

- [../kb/references/retrieval-authoring.md](../kb/references/retrieval-authoring.md)
  (on-demand: drafting a page in `gaps`) — how to write Markdown the corpus
  chunks and ranks well. `srd:kb` owns it.
- [../create/references/doc-corpus.md](../create/references/doc-corpus.md)
  (on-demand: before the first corpus lookup in `gaps`) — how to reach the
  corpus, including the host the REST mirror answers on. `srd:create` owns it;
  the `search`/`get_doc` calls below are specified there, not here.

## Backends

The KB lists read `_open-questions.md` at the KB root, which `srd:kb` resolves:
one row per question under `## Open` (label, kind `deferred` or `unknown`, date
raised, hit count, `Lives in` page link) or `## Closed`. The wording lives in
the page's `## Open questions` section; a row with an empty page link has only
its label. Without a KB root, say so and work `gaps` alone.

The `gaps` list reaches the store by, in priority order — falling through only
when a step is genuinely absent, never because one call failed. Absent means
the tool is not in the tool set, or the mirror's host does not answer at all; a
call that reaches the store and returns an error is a working store with a
problem, and is reported rather than retried or fallen past:

1. MCP — `mcp__srd-doc__list_gaps` (optional `status`),
   `mcp__srd-doc__resolve_gap` (`gap_id`, `published_url`, optional `note`);
   the read tools `search`, `get_doc`, `list_docs` come from the same server.
2. The REST mirror — `GET /gaps?status=open`, `POST /gaps/{id}/resolve` with
   `{"published_url": "…", "note": "…"}`; `GET /search?q=…&k=5`,
   `GET /docs/<id>`.

Fall through only when a step genuinely is not there, not on one failed call.
If neither exposes `/gaps`, the store is not enabled — say so and work the KB
lists alone.

A gap record carries `id`, `status`, `created_at`, `kind`
(missing/wrong/incomplete/ambiguous), `topic`, `doc_id`, `heading_path`,
`source_url`, `demand`, `target_claim`, `detail`, `search_terms`, `srd_ref`.
Empty `doc_id`/`heading_path`/`source_url` mean the reporter found nothing
relevant.

## Workflow

The first token names one list, or `all` (default). Copy this checklist and
tick it off:

- [ ] 1. Open the sitting: resolve both backends, count each list, stop for
      the user's pick. Skipped when a list was named.
- [ ] 2. `deferred`: ask, hand the answer to `srd:kb`.
- [ ] 3. `unknowns`: triage, never answer.
- [ ] 4. `gaps`: cluster, check the corpus, grill, draft, resolve.

Work one list at a time in the user's chosen order; close each item through its
own mechanism, one call per item.

### 1. Open the sitting

State the counts in one line and stop. With a backend missing, state the counts
you have and name the list you cannot see in the same line — two counts and
"no gap store configured" is the opening for that sitting, not a reason to
skip the opening or to stop. Lead with `deferred` when it is non-empty: a
sitting that opens with quick closes keeps going. All three empty:
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

Establish each row's state from the user in the room, never from the corpus. An
unknown is by definition something nobody has pinned down, so a corpus hit that
looks like the answer is either a different question or the very thing that
should have closed it long ago — say so and let the user decide which. Reading
one as the answer is how an unknown gets closed with a guess wearing a source.

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

1. List open gaps (`list_gaps` with `status: open`, or `GET /gaps?status=open`).
2. Cluster the gaps one page would resolve — same `doc_id`, same
   `heading_path`, or one topic phrased differently. Rank by cluster size:
   repeated reports mean higher priority. The user picks one; work one at a
   time.
3. Check the corpus: `search` each gap's `search_terms`, `get_doc` any cited
   `doc_id`. Genuinely absent content needs new prose; present-but-unranked
   content needs a structural edit to the existing page, never a duplicate
   (the reference's "Absent vs unfindable").
4. Extract what the page must state. A record says what is missing, not what
   is true; one filed in heavy mode already carries knowledge in
   `detail`/`target_claim` — read those first as a starting point, not gospel.
   Run `craft:grill-me` on the cluster to fill what the record leaves open,
   never re-asking what it answers. Do not draft from guesses.
5. Draft one page (or the edit to an existing one) against
   [../kb/references/retrieval-authoring.md](../kb/references/retrieval-authoring.md),
   to a neutral drafts location the user names, outside every corpus source —
   the KB root included: a draft inside a source is clobbered by the next sync
   and pollutes the index. Unsure whether a path is outside every source: ask
   which directories are sources first.
6. Resolve once the human gives the published URL: `resolve_gap` for every gap
   in the cluster, so each moves from `open` to `resolved` with the URL
   recorded. Say that the corpus reflects the page only after the next sync
   and server restart.

A platform fact the grill surfaces also goes to `srd:kb`; the gap and the KB
entry close independently.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. Counts and what closed are enough — never
re-print a drafted page or the rows just moved.

## Self-learning

Obey this skill's lessons when it has any: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/srd/backlog.md` when this directory is
read-only. Most runs have none; absence is the normal case and needs no
comment. On a correction or self-caught mistake, append a one-line rule to
whichever path is writable, creating it, and report where.
