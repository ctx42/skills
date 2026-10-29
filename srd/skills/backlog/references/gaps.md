# gaps

The `gaps` list's procedure: get each gap's fact into a corpus section, then
record the section on the gap. Read when working `gaps`, or when any list
fills a gap (step 6).

1. List open gaps with empty `answer` (`list_gaps` with `status: open`). A
   partly filled one owes only what its `detail` says remains.
2. Cluster the gaps one section would fill — same `doc_id`, same
   `heading_path`, or one topic phrased differently. Rank by cluster size and
   `hits`: repeated reports and encounters mean higher priority. The user picks
   one; work one at a time.
3. Check the corpus: `search` each gap's `search_terms`, `get_doc` any cited
   `doc_id`. Genuinely absent content needs new prose — added to the existing
   page when it is partly present there; present-but-unranked content needs a
   structural edit to the existing page, never a duplicate ("Absent vs
   unfindable" in `retrieval-authoring.md`). A section already stating the
   whole fact fills the cluster now (step 6), with no draft.
4. Extract what the section must state. A record says what is missing, not what
   is true — but some were grilled at depth when filed and already carry
   knowledge in `detail` and `target_claim`. Spot them by a populated
   `target_claim`, read those first as a starting point, not gospel.
   Run `craft:grill-me` on the cluster to fill what the record leaves open,
   never re-asking what it answers. Do not draft from guesses: every sentence
   of the draft is something the user confirmed or the corpus states — a
   gap's own claim is the reporter's word until the user confirms it, and a
   draft states no consequence or summary neither source gave. A sentence
   the corpus states is shown to the user with its source line ("Citing a
   source" in `doc-corpus.md`) before the draft or the `srd:kb` hand-off; a
   section that fills a gap, in the question that asks the user to confirm the
   fill.
5. Write the fix where the user picks:
   - KB: hand the confirmed fact to `srd:kb`, which writes it to its inbox; it
     fills only once `srd:kb` files it into a topic page.
   - Doc page: draft one page (or the edit to an existing one) against
     `retrieval-authoring.md`, to a neutral drafts location the user names,
     outside every corpus source — the `kb` folder included: a draft inside a
     source is clobbered by the next sync and pollutes the index. The sources
     are the top-level folders the `list_docs` paths start with; unsure
     whether a path is outside them, ask. A human publishes it; it fills only
     once pulled into the corpus.
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
