---
name: backlog
description: >
  Works the open backlog of everything the documentation and the knowledge base
  still owe: questions deferred during SRD work, facts nobody has pinned down,
  and reported gaps, facts the corpus does not supply reliably. Use when asked
  to work the backlog, clear open questions, answer what was deferred, or write
  up and fill reported documentation gaps.
argument-hint: "[all*|deferred|unknowns|gaps]"
license: MIT
---

# backlog

## Usage

```
/backlog           all three lists, cheap wins first (default)
/backlog deferred  questions someone knows the answer to; closed by asking
/backlog unknowns  things nobody has pinned down; triage, not answering
/backlog gaps      reported corpus gaps; drafts the fix, fills from the corpus
```

One sitting over the three lists the SRD skills fill as a byproduct, cheap wins
first.

| List        | Says                        | Closed by               |
|-------------|-----------------------------|-------------------------|
| `deferred`  | someone knows; no time then | asking, right now       |
| `unknowns`  | nobody has pinned it down   | deciding or finding out |
| `gaps`      | the corpus falls short      | a corpus section        |

All three are open gaps in the server's store, told apart by `answer`:
`deferred`, `unknown`, or empty for a plain gap. Each closes only when a corpus
section states its fact: a KB topic page or a pulled doc page. A URL, or a
draft not yet pulled, never closes one.

The lists are not interchangeable: a deferred gap closes by asking, an unknown
by a decision or a finding, a plain gap by authorship. Never draft a page for a
fact nobody has given.

## Boundaries

- Role: the consumer end of every backlog — list, triage, extract, close.
- Must not: write any file under the `kb` folder (`srd:kb` owns it; every
  knowledge-base write is delegated there); publish anywhere; author or edit
  an SRD; file new gaps (`srd:report-doc-gap` owns that, the sweep's
  included).
- Depends on: `srd:kb` for every KB write, `srd:report-doc-gap` for the
  sweep's gaps, the server's gap store for all three lists.

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

The lists use the server's gap tools on `mcp__<mcp-server>__`: `list_gaps`
(optional `status`, `srd_ref`, `stale`, ranked `query`), `update_gap` (`gap_id`,
`answer`), `fill_gap` (`gap_id`, `filled_by`, `complete`, optional
`remaining`), `reopen_gap` and `wontfix_gap` (`gap_id`, `reason`); the read
tools `search`, `get_doc`, `list_docs` come from the same server. One
`list_gaps` with `status: open` feeds all three lists, split by `answer`. An
error from a call is a store that exists and is unwell: report it with its
message and stop; never retry it or work around it. Stop means the sitting
ends there, sweep and re-check included: no later step or list runs.

A gap record carries `id`, `status`, `kind`
(missing/wrong/incomplete/ambiguous), `answer` (deferred/unknown/empty),
`topic`, `demand`, `detail`, `target_claim`, `doc_id`, `heading_path`,
`search_terms`, `srd_ref`, `hits` (encounters in SRD work), `created`, and
`filled_by` (`ref`, `hash`); a stale one adds `stale: true` and `stale_refs`
(`ref`, `reason`: `changed`, `vanished`, `unhashed`). Empty
`doc_id`/`heading_path` mean the reporter found nothing relevant. Statuses:
`draft`, `open` (partly filled when `filled_by` is set; `detail` says what
remains), `filled`, `wontfix`. A `draft` is still `srd:report-doc-gap`'s —
never in this backlog.

## Workflow

The first token names one list, or `all` (default). Copy this checklist and
tick it off:

- [ ] 0. Pass the gate. Always, before anything below.
- [ ] 1. Sweep `REJECTED` SRDs. Always, any list named.
- [ ] 2. Re-check stale gaps. Always, any list named.
- [ ] 3. Open the sitting: count each list, stop for the user's pick. Skipped
      when a list was named.
- [ ] 4. `deferred`: ask, hand the answer to `srd:kb`, fill once a topic page
      states it.
- [ ] 5. `unknowns`: triage, never answer.
- [ ] 6. `gaps`: cluster, check the corpus, grill, write the fix, fill or
      wontfix.

Work one list at a time; a pick names one list, and when it is done offer the
next non-empty one in a line naming only that list — what closed waits for the
closing line. Close each item through its own mechanism, one call per
item.

### 1. Sweep REJECTED SRDs

An SRD whose `Status` is `REJECTED` is abandoned: the KB facts it attested are
suspect until someone checks them.

1. `list_docs`; `get_doc` each SRD under the `initiatives` folder (not its
   `.review.md` or `.questions.md` companions) and read the `Status` field of
   its metadata block. Keep the folder of each `REJECTED` one; none, the sweep
   ends silently.
2. `get_doc` each page under the `kb` folder; keep every section whose
   attestation line names a rejected folder. A page whose `srd_ref` names it
   while no attestation line does is one section: its `#` heading.
3. Per rejected folder, `list_gaps` with `status: open` and `srd_ref` the
   folder: an open `wrong` gap with the section's `doc_id` and `heading_path`
   already reverts it — skip the section, no hit.
4. Hand each remaining section to `srd:report-doc-gap` as
   [an abandoned SRD's](../report-doc-gap/SKILL.md#a-cut-requirement) gap:
   `doc_id` and `heading_path` the section, `srd_ref` the folder, `detail`
   naming the rejected SRD and every other SRD the attestation line names. The
   `REJECTED` Status is the confirmation: no proposal, no grill; it files each
   open at once. Never edit the section.

The sweep is one clause of the opening counts line, or the reply's first line
when a list was named: `wishlist-v2 REJECTED: 2 gaps filed, 1 already open`.
No `REJECTED` SRD, no clause. Its gaps are plain open gaps: count them in
`gaps`.

### 2. Re-check stale gaps

A stale gap cites a section that changed or vanished since the fill, or was
never hashed; the server flags it and never changes its status. End with each
one refreshed or open; only an open gap with no ref left that holds stays
flagged, since `fill_gap` needs one.

1. `list_gaps` with `stale: true`; none, the re-check ends silently.
2. Per gap, `get_doc` each `filled_by` ref's document; for a `vanished` ref,
   `search` the gap's `search_terms` for where the fact moved. Judge each ref
   against the gap's `target_claim`, else its `detail`: does the section still
   state its part of the fact, in any wording?
3. One call per gap; a filled gap's list must resolve in full:
   - Every ref still states it: `fill_gap` with the same `filled_by` —
     `complete: true` refreshes a filled gap, `complete: false` re-hashes an
     open one.
   - A ref vanished and the fact moved: `fill_gap` with the new ref in its
     place, `complete` as above.
   - A filled gap's section no longer states its part: when the other refs
     still state the whole fact, `fill_gap` them, `complete: true`; else
     `reopen_gap`, `reason` what changed; it joins `gaps`.
   - An open gap's section no longer states it: `fill_gap` the refs that
     still hold, `complete: false`, `remaining` adding the lost part; none
     hold: no call, name it in the report as still stale.
4. Unsure whether a section still states the fact: ask the user then, before
   the counts line, one question per gap, quoting the section beside the
   claim; act on the answer as step 3 says. Never refresh on a guess: a
   refresh re-vouches the section.

The re-check is one clause of the opening counts line, or the reply's first
line when a list was named: `stale: 2 refreshed, 1 reopened`. No stale gap,
no clause.

### 3. Open the sitting

State the counts in one line and stop. Lead with `deferred` when it is
non-empty: a sitting that opens with quick closes keeps going. All three empty:
say the backlog is clear and stop.

### 4. deferred

Take the deferred gaps one at a time, oldest `created` first. Ask the question
its `detail` words.

- Answered: hand the fact to `srd:kb` with the gap's id, then `update_gap`
  `answer: ""` — asked and answered, it owes only a corpus section now and
  joins `gaps`. `srd:kb` writes to its inbox, never a fill target: offer
  `/kb file`, and fill as step 6 of `gaps` says once a topic page states it.
- "Still not now": leave it; do not re-ask it this sitting.
- No answer exists: it is an unknown, not a skip — `update_gap` with
  `answer: unknown`, and say so.

### 5. unknowns

Only the user closes an unknown. You may read the corpus — an unknown that
turns out to be documented is worth knowing — but a hit is evidence to put in
front of them, never a closure. It is either about a different question, or the
very thing that should have closed this gap long ago, and only they can say
which. Reading one as the answer is how an unknown gets closed with a guess
wearing a source. Bring the hit, name what it does and does not settle, and let
them decide.

For each unknown gap:

- Answered since (a decision was taken, or someone found out): handled as an
  answered deferred gap — the fact goes to `srd:kb`, then `answer: ""`.
- The user confirms a corpus hit states the answer: no `srd:kb` hand-off —
  `fill_gap` on that section per step 6 of `gaps`; its `answer` needs no reset.
- Still open: confirm and move on. Bump nothing — `hits` tracks encounters
  during SRD work, not reviews.
- Moot (the feature changed, the subject went away): on the user's word,
  `wontfix_gap` with `reason` why, so it is not re-opened.

Never invent an answer to close a gap: an unknown left open is correct; one
closed with a guess is a fact the corpus will serve as truth.

### 6. gaps

Get each gap's fact into a corpus section, then record the section on the gap.

1. List open gaps with empty `answer` (`list_gaps` with `status: open`). A
   partly filled one owes only what its `detail` says remains.
2. Cluster the gaps one section would fill — same `doc_id`, same
   `heading_path`, or one topic phrased differently. Rank by cluster size and
   `hits`: repeated reports and encounters mean higher priority. The user picks
   one; work one at a time.
3. Check the corpus: `search` each gap's `search_terms`, `get_doc` any cited
   `doc_id`. Genuinely absent content needs new prose — added to the existing
   page when it is partly present there; present-but-unranked content needs a
   structural edit to the existing page, never a duplicate (the reference's
   "Absent vs unfindable"). A section already stating the whole fact fills the
   cluster now (step 6), with no draft.
4. Extract what the section must state. A record says what is missing, not what
   is true — but some were grilled at depth when filed and already carry
   knowledge in `detail` and `target_claim` (`srd:report-doc-gap` calls that a
   heavy grill). Spot them by a populated `target_claim`, read those first as a
   starting point, not gospel.
   Run `craft:grill-me` on the cluster to fill what the record leaves open,
   never re-asking what it answers. Do not draft from guesses: every sentence
   of the draft is something the user confirmed or the corpus states — a
   gap's own claim is the reporter's word until the user confirms it, and a
   draft states no consequence or summary neither source gave.
5. Write the fix where the user picks:
   - KB: hand the confirmed fact to `srd:kb`, which writes it to its inbox; it
     fills only once `srd:kb` files it into a topic page.
   - Doc page: draft one page (or the edit to an existing one) against
     [../kb/references/retrieval-authoring.md](../kb/references/retrieval-authoring.md),
     to a neutral drafts location the user names, outside every corpus source
     — the `kb` folder included: a draft inside a source is clobbered by the
     next sync and pollutes the index. The sources are the top-level folders
     the `list_docs` paths start with; unsure whether a path is outside them,
     ask. A human publishes it; it fills only once pulled into the corpus.
6. Fill once a corpus section states the fact and `get_doc` shows it:
   `fill_gap` for every gap in the cluster, `filled_by` each stating section
   as `<identity>#<slug>` (`kb/users-and-access.md#customer-and-project-timezones`,
   `1882030917#cold-storage`) — the identity is the result's `id` from
   `search` or `list_docs`, copied as is, never its `path`; the slug is the
   section's heading slug. `complete: true` when the sections state the
   whole fact; when they state part, `complete: false` with `remaining` saying
   what is still missing, and the gap stays open. A URL never fills a gap. When
   the page is published but not yet pulled, or nobody can publish in this
   sitting, fill nothing: say where the draft is and that the gaps stay `open`
   until the pull brings the page into the corpus, plus a server restart
   unless the server watches its sources. Never fill against `_inbox.md`: its
   heading slugs break on the next `/kb file`. Never fill against an unconfirmed
   fact.
7. Wontfix only on the user's decision that the corpus will not carry the fact
   (out of product scope, superseded): `wontfix_gap` for every gap in the
   cluster, `reason` that decision. Never to clear the list.
8. Reopen a `filled` gap whose sections no longer state its fact — the user
   says so, or a lookup shows it: `reopen_gap` with `reason` what changed. It
   rejoins the open list with its `filled_by` kept, to fill again with a
   corrected list.

A platform fact the grill surfaces also goes to `srd:kb`, unless this sitting
publishes a page that states it: the KB holds only what the docs do not. Once
`srd:kb` files it into a topic page, that section fills the gap.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. Counts and what closed are enough — never
re-print a drafted page or the gaps just changed.

Name `srd:kb` as the writer whenever a page changed, as a count
per delegate: this skill writes nothing under the `kb` folder, and a report
that says "closed two" without saying who wrote them reads as though it did.
Never say what the answers were or where they landed, in any shape — the user
gave them minutes ago. Wrong: `srd:kb saved 2 answers (3.4 V threshold, 6-hour
uploads)`, or "the threshold (3.4 V) is now on `kb/logger.md`". Right:
`srd:kb: 2 answers`.

"What closed" is said once per sitting, in the closing line — not again as each
list finishes, and not restated in two shapes ("`gap-0010`, `gap-0015`
filled" and "1 cluster closed (2 gaps)") in the same breath. Name partly
filled gaps apart from filled ones (`gap-0003` partly filled): it still owes a
section.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/srd/backlog.md`, the
sibling winning a conflict — a read-only install writes the second, and what it
learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule to the sibling when this directory
is writable, else to the fallback, creating it, and report where.