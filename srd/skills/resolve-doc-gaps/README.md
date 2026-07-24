# resolve-doc-gaps

Closes the **documentation-gap loop**. SRD-authoring sessions report gaps —
missing, wrong, incomplete, or ambiguous docs — to the `srd-doc` server through
`report_gap`. This skill works that backlog: it lists the gaps, clusters the
ones a single article can cover, interviews you for the missing knowledge,
drafts a retrieval-friendly Markdown page, and records the published URL once
you paste the page into Confluence.

It is a **consumer** skill: it turns reported gaps into a publishable draft. It
does not report gaps (that is `srd:create` / `srd:system-check`), does not
publish to Confluence, and never writes into the corpus.

## Usage

```
/resolve-doc-gaps   list, cluster, draft, and resolve the doc-gap backlog (default)
```

## When to Use

- You want to work the doc-gap backlog the `srd-doc` server has collected.
- You have one or more reported gaps and want a publishable page that fills
  them.
- You have published a page and want the gaps it covers marked resolved.

## How It Works

1. **Confirms the gap channel** — the `list_gaps` / `resolve_gap` MCP tools, or
   the `/gaps` REST endpoints. If the server has no gap store, it stops.
2. **Lists** the open gaps and summarizes the backlog.
3. **Clusters** gaps one page would resolve (same document, section, or topic);
   duplicate reports raise a cluster's priority. You pick a cluster.
4. **Checks the corpus** with `search` / `get_doc` to tell genuinely absent
   content (write new prose) from present-but-unfindable content (a structural
   edit to an existing page).
5. **Extracts the knowledge** with `craft:grill-me` — the gaps say what is
   missing; only you hold the facts, so it interviews you until every gap has a
   concrete answer.
6. **Drafts** the page against the retrieval-authoring conventions
   (`references/retrieval-authoring.md`), written to a neutral path **outside
   every corpus source** so cfsync never clobbers it and it never pollutes the
   index.
7. **Resolves** every gap in the cluster with the URL once you publish to
   Confluence by hand.

## What to Expect

- A shortlist of open gaps, clustered, with duplicates flagged as priority.
- A Markdown draft at a path you name, outside the corpus, ready to paste into
  Confluence — never written into a corpus source directory.
- Each worked gap moved from `open` to `resolved` with its published URL
  recorded. The corpus reflects the new page only after the next cfsync +
  server restart.

## Evaluations

### 1. No gap store configured

**Request:** `/resolve-doc-gaps` against a retrieval-only server.

**Expected behavior:**
- Probes for `list_gaps` / `GET /gaps`, finds neither, and stops with a clear
  message that the gap channel is not enabled — no draft, no error loop.

### 2. Cluster and draft

**Request:** `/resolve-doc-gaps` with three open gaps, two of them the same missing fact
reported by different sessions.

**Expected behavior:**
- Lists the open gaps and groups the two duplicates into one cluster, noting the
  repeat as a priority signal.
- Runs `craft:grill-me` to extract the facts before drafting; does not invent
  content from the gap text alone.
- Produces a page with keyword-rich `##` headings, a descriptive title with
  `aliases`, and each `target_claim` as an explicit sentence.
- Writes the draft to a user-named path outside every corpus source, and refuses
  (asks first) if the path is inside a source directory.

### 3. Present-but-unfindable

**Request:** A gap whose `search_terms` are absent from the corpus, but a
`get_doc` on its `doc_id` shows the fact is actually documented.

**Expected behavior:**
- Recognizes the fact exists but does not rank, and drafts a structural edit —
  heading rename, `aliases`, an explicit fact sentence — to the existing page
  rather than a duplicate article.

### 4. Resolve after publish

**Request:** After the user publishes the drafted page and gives its Confluence
URL.

**Expected behavior:**
- Calls `resolve_gap` for every gap in the cluster with the published URL, so
  each moves to `resolved`.
- States that the corpus reflects the page only after the next cfsync + restart;
  does not claim search now finds it.
