# Authoring a page for retrieval

<!-- MIRRORED FILE — these rules mirror srd-mcp-doc/docs/authoring.md, which
     documents the indexer that actually chunks and ranks these pages. Mirrored
     from commit 538eb93 (2026-07-14). The copy is deliberate: the skills must
     work without the server repo checked out. When the server's chunking or
     ranking changes, update this file and bump the commit above — otherwise
     every page written against it chunks or ranks wrongly, and silently. -->

Pages written for the `srd-doc` corpus — knowledge-base pages, and doc-gap
drafts — are retrieved by **BM25 keyword search over section chunks**, with no
semantic matching. A page is found only by the words it contains and ranked by
where those words sit. Apply these rules to everything written for the corpus so
it indexes and ranks well.

## Headings

- Break sections with `#` or `##`, not `###`+ — only level-1 and level-2
  headings start a new chunk; deeper headings just extend the heading path.
- Make every `#`/`##` heading keyword-rich — headings index into a boosted
  field, so a term in a heading outranks the same term in the body. No vague
  `Overview`.
- Split a section over ~800 tokens into focused sub-`##` sections, one topic
  each.

## Title and names

- Give the page a descriptive title — it indexes into the boosted title field
  for every chunk.
- Name the file/page for its topic; `_`, `-`, and `/` split into searchable
  terms.
- Declare synonyms once in front-matter `aliases` (they index as extra title
  terms), not sprinkled through prose. Do not hand-write plural/tense variants
  — the index stems English.

## Facts

- State each capability as an explicit sentence — an agent verifies a claim by
  searching for its words. For a doc-gap draft, write the gap's exact
  `target_claim` as a plain declarative sentence.
- Prefer one canonical term per concept; scattered names split matches.
- Keep glossary-style definitions one per `##` heading.

## Links and tables

- Put the canonical URL first in the body — a citation uses the first
  `atlassian.net` link, else the first `http(s)` URL.
- Give tables real column headers and a one-line caption sentence; bare pipe
  cells tokenize poorly.

## Absent vs unfindable

A live `search`/`get_doc` check on the fact's own words (a gap's
`search_terms`, for a doc-gap draft) tells you which fix the page needs:

- **Genuinely absent** — nothing relevant exists. Write new prose.
- **Present but unranked** — the fact is there but the search terms miss it.
  The fix is structural: rename the section heading to carry the query words,
  add `aliases`, and restate the fact as an explicit sentence. Draft the edit
  to the existing page, not a duplicate.
