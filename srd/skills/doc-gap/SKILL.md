---
name: doc-gap
description: >
  Closes the documentation-gap loop: lists gaps reported to an mcp-doc server,
  clusters related ones, extracts the missing knowledge from the user, drafts a
  retrieval-friendly Markdown page, and records the published URL on resolve.
  Use when asked to work the doc-gap backlog, write up reported documentation
  gaps, or resolve a gap.
license: MIT
---

# doc-gap

Close the loop opened by `report_gap`: turn reported documentation gaps into a
publishable page. SRD-authoring sessions file gaps (via `srd:create` and
`srd:system-check`); this skill lists them, clusters what one article can
cover, extracts the missing facts from the user, drafts the page, and records
where the human published it.

## Boundaries

- **Role:** consumer of the doc-gap backlog. List and cluster gaps, draft the
  page that fills them, and record the resolution.
- **Must not:** publish to Confluence — the human authors the page there by
  hand; this skill only drafts and records the URL. Never write a draft into a
  corpus source directory (cfsync would clobber it and it would pollute the
  index). Never edit the corpus or author an SRD (that is `srd:create`).
- **Depends on:** an `mcp-doc` server configured with a gap store — the
  `list_gaps` / `resolve_gap` tools (or the `/gaps` REST endpoints). If the gap
  channel is absent, stop and tell the user; there is nothing to work.

## Sources of truth

- [references/retrieval-authoring.md](references/retrieval-authoring.md)
  (on-demand: step 3) — how to write a page so the BM25 corpus indexes and
  ranks it well. Mirrors the server's own `docs/authoring.md`. Draft against
  it.

## The gap channel

The same `mcp-doc` server that serves the corpus accepts and returns gaps when
it is configured with a gap store. Reach the channel by, in priority order:

1. **MCP gap tools** — `list_gaps` (optional `status`), `resolve_gap`
   (`gap_id`, `published_url`, optional `note`), e.g. `mcp__<name>__list_gaps`.
   Preferred. The read tools `search`, `get_doc`, `list_docs` come from the
   same server — use them to check what the corpus already holds.
2. **REST mirror** — same server, when MCP is not wired into this client:
   `GET /gaps?status=open`, `POST /gaps/{id}/resolve` with a JSON body
   `{"published_url": "…", "note": "…"}`; `GET /search?q=…&k=5`,
   `GET /docs/<id>`.

Fall through only when a step genuinely is not there, not on one failed call.
If neither exposes `/gaps`, the store is not enabled — stop.

A gap record carries: `id`, `status`, `kind`
(missing/wrong/incomplete/ambiguous), `topic`, `doc_id`, `heading_path`,
`source_url`, `demand`, `target_claim`, `detail`, `search_terms`, `srd_ref`.
Empty `doc_id`/`heading_path`/`source_url` mean the reporter found nothing
relevant; populated ones point at the page the gap is about.

## Workflow

Copy this checklist and tick it off:

- [ ] 0. Confirm the gap channel is reachable; else stop.
- [ ] 1. List the open gaps.
- [ ] 2. Cluster the gaps one article can cover; pick one cluster with the user.
- [ ] 3. Extract the missing knowledge with `craft:grill-me`.
- [ ] 4. Draft the page to a neutral path outside every corpus source.
- [ ] 5. On the user publishing to Confluence, resolve every gap in the cluster.

### 0. Confirm the channel

Resolve the backend (see [The gap channel](#the-gap-channel)). If neither
`list_gaps` nor `GET /gaps` exists, the store is not enabled — say so and stop.

### 1. List

List open gaps: `list_gaps` with `status: open` (or `GET /gaps?status=open`).
With none open, report that the backlog is empty and stop. Otherwise summarize
the backlog: count, and the topics/`doc_id`s in play.

### 2. Cluster

Group gaps that **one page would resolve** — same `doc_id`, same
`heading_path`, or the same underlying `topic` phrased differently. Duplicates
are signal, not noise: repeated reports of the same gap mean higher priority,
so surface a cluster's size when ranking. Present the clusters and let the user
pick which one to work; work one cluster at a time.

For the chosen cluster, check what the corpus already holds before writing:
`search` each gap's `search_terms`, and `get_doc` any cited `doc_id`. This
tells you **absent vs unfindable** (see the reference): genuinely missing
content needs new prose; present-but-unranked content needs a structural edit
to the existing page, not a duplicate.

### 3. Extract the knowledge

The gap records say what is missing, not what is true — only the user holds the
facts. Run `craft:grill-me` on the cluster to pull out exactly what the page
must state: each gap's `target_claim` confirmed or corrected, the surrounding
context a reader needs, and any terms/synonyms. Grill until every gap in the
cluster has a concrete, verifiable answer; do not draft from guesses.

### 4. Draft

Draft one Markdown page (or the edit to an existing page, for the unfindable
case) applying every rule in
[references/retrieval-authoring.md](references/retrieval-authoring.md):
keyword-rich `#`/`##` headings, a descriptive title with `aliases`, each
resolved `target_claim` written as an explicit declarative sentence, canonical
URL first, captioned tables.

**Write the draft outside every configured corpus source.** A draft inside a
source directory would be clobbered by the next cfsync and would pollute the
index. Write to a neutral drafts location the user names; if you cannot confirm
a path is outside the corpus, ask which directories are sources before writing.
The draft is staging for a human to paste into Confluence — it never becomes a
corpus file directly.

### 5. Resolve

The human publishes the page to Confluence by hand; this server cannot push up.
Once they give you the published URL, call `resolve_gap` for **every gap in the
cluster** — `{ gap_id, published_url, note? }` (or
`POST /gaps/{id}/resolve`) — so each moves from `open` to `resolved` with the
URL recorded. The corpus itself reflects the new page only after the next
cfsync + server restart, exactly as any other corpus change; say so.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/srd/doc-gap.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
